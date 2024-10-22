document.getElementById('upload-form').onsubmit = async function(event) {
    event.preventDefault();

    const files = document.getElementById('video-files').files;
    const fileNames = Array.from(files).map(file => file.name); // Récupération des noms des vidéos
    const statusDiv = document.getElementById('status');

    // Appel à la Lambda pour obtenir les URL pré-signées
    const response = await fetch('https://YOUR_API_LAMBDA_URL/presigned-urls', {
        method: 'POST',
        body: JSON.stringify({ video_names: fileNames }),
        headers: { 'Content-Type': 'application/json' }
    });
    
    const data = await response.json();
    const uploadUrls = data.upload_urls;

    // Téléverser chaque fichier avec son URL pré-signée
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const uploadUrl = uploadUrls[i].upload_url;
        
        try {
            const result = await fetch(uploadUrl, {
                method: 'PUT',
                body: file
            });
            statusDiv.innerHTML += `<p>${file.name} téléversé avec succès</p>`;
        } catch (err) {
            statusDiv.innerHTML += `<p>Erreur lors du téléversement de ${file.name} : ${err.message}</p>`;
        }
    }
};
