// Main JavaScript functionality for the Agriculture Knowledge Search

async function performSearch() {
    const q = document.getElementById("q").value.trim();
    if (!q) {
        showMessage("Please enter a search query", "error");
        return;
    }
    
    const resultsDiv = document.getElementById("results");
    const loadingDiv = document.getElementById("loading");
    
    resultsDiv.innerHTML = "";
    loadingDiv.style.display = "block";
    
    try {
        const res = await fetch(`/search?query=${encodeURIComponent(q)}`);
        const data = await res.json();
        
        loadingDiv.style.display = "none";
        
        if (data.length === 0) {
            resultsDiv.innerHTML = `
                <div class="status">
                    <p><em>No results found. Try different keywords or crawl the websites first.</em></p>
                </div>
            `;
            return;
        }
        
        data.forEach(d => {
            resultsDiv.innerHTML += `
                <article>
                    <a href="${d.url}" target="_blank">${d.title}</a>
                    <p>${d.snippet}</p>
                    <small>
                        Relevance Score: ${d.score} | 
                        <a href="${d.url}" target="_blank">View Source</a>
                    </small>
                </article>
            `;
        });
    } catch (error) {
        loadingDiv.style.display = "none";
        showMessage("Error performing search. Please try again.", "error");
        console.error("Search error:", error);
    }
}

async function startCrawl() {
    const msgSpan = document.getElementById("crawlmsg");
    const crawlButton = document.querySelector("#crawl button");
    
    msgSpan.innerText = "🔄 Crawling... this may take a few minutes";
    crawlButton.disabled = true;
    crawlButton.style.opacity = "0.6";
    
    try {
        const res = await fetch("/crawl", { method: "POST" });
        const j = await res.json();
        
        if (j.status === "completed") {
            msgSpan.innerText = `✅ Done. Pages crawled: ${j.pages_crawled}`;
            showMessage(`Successfully crawled ${j.pages_crawled} pages!`, "status");
        } else {
            msgSpan.innerText = "❌ Error during crawling";
            showMessage("Error during crawling. Please try again.", "error");
        }
    } catch (error) {
        msgSpan.innerText = "❌ Error during crawling";
        showMessage("Error during crawling. Please try again.", "error");
        console.error("Crawl error:", error);
    } finally {
        crawlButton.disabled = false;
        crawlButton.style.opacity = "1";
    }
}

async function checkStatus() {
    try {
        const res = await fetch("/status");
        const data = await res.json();
        
        if (data.status === "running") {
            const statusDiv = document.getElementById("status");
            if (statusDiv) {
                statusDiv.innerHTML = `
                    <div class="status">
                        <strong>System Status:</strong> Running<br>
                        <strong>Documents:</strong> ${data.documents}<br>
                        <strong>Vectors:</strong> ${data.vectors}
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error("Status check error:", error);
    }
}

function showMessage(message, type = "status") {
    const messageDiv = document.createElement("div");
    messageDiv.className = type;
    messageDiv.innerHTML = `<p>${message}</p>`;
    
    const container = document.querySelector(".container");
    container.insertBefore(messageDiv, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    }, 5000);
}

// Event listeners
document.addEventListener("DOMContentLoaded", function() {
    // Allow Enter key to trigger search
    document.getElementById("q").addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            performSearch();
        }
    });
    
    // Check status on page load
    checkStatus();
    
    // Add smooth scrolling for better UX
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Add loading animation for better UX
function showLoading(element) {
    element.style.position = 'relative';
    element.innerHTML += '<div class="loading-spinner"></div>';
}

function hideLoading(element) {
    const spinner = element.querySelector('.loading-spinner');
    if (spinner) {
        spinner.remove();
    }
} 