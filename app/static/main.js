function deleteFeature(id) {
    fetch(`/features/${id}`, { method: 'DELETE' })
        .then(res => {
            if (res.ok) location.reload();
            else alert("Error deleting feature");
        });
}
