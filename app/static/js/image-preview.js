document.querySelectorAll('input[type="file"][data-preview]').forEach((input) => {
  input.addEventListener('change', () => {
    const file = input.files && input.files[0];
    const image = document.getElementById(input.dataset.preview);
    if (!file || !image || !file.type.startsWith('image/')) return;
    const previewUrl = URL.createObjectURL(file);
    image.src = previewUrl;
    image.hidden = false;
    image.parentElement.querySelectorAll(':scope > span').forEach((span) => { span.hidden = true; });
    image.onload = () => URL.revokeObjectURL(previewUrl);
  });
});
