const loader = document.querySelector("[data-loader]");

function showLoader(text = "Processing...") {
    if (!loader) return;
    loader.hidden = false;
    loader.classList.add("is-visible");
    loader.querySelector("p").textContent = text;
}

function hideLoader() {
    if (!loader) return;
    loader.classList.remove("is-visible");
    loader.hidden = true;
}

document.addEventListener("DOMContentLoaded", () => {

    hideLoader();

    document.querySelectorAll("[data-loading-form]").forEach(form => {

        form.addEventListener("submit", function(e){

            const file = this.querySelector("input[type=file]");
            const method = (this.getAttribute("method") || "get").toLowerCase();

            if(file){

                if(file.files.length === 0){

                    e.preventDefault();
                    alert("Please choose a photo first.");
                    return;

                }

                showLoader("Uploading & Indexing...");

            }else if(method === "post"){

                showLoader("Reindexing Gallery...");

            }

        });

    });

});

window.addEventListener("pageshow", hideLoader);
