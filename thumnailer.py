from PIL import Image
import os
import json
from multiprocessing import Pool, Manager, cpu_count

CACHE_FILE = "thumbnail_cache.json"

def load_cache():
    """Load the cache from a file or return an empty dictionary if the file is empty or invalid."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If the file is invalid, reinitialize it
            print(f"Warning: {CACHE_FILE} is empty or corrupt. Reinitializing cache.")
            return {}
    return {}


def save_cache(cache):
    """Save the updated cache to a file."""
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)


def generate_thumbnail(image_info):
    image_path, output_dir, size, valid_cache = image_info

    try:
        # Determine thumbnail path
        base_name = os.path.basename(image_path)
        thumbnail_path = os.path.join(os.path.abspath(output_dir), f"thumb_{base_name}")

        # Check cache and modification times
        if thumbnail_path in valid_cache and valid_cache[thumbnail_path] == image_path:
            try:
                if os.path.getmtime(image_path) <= os.path.getmtime(thumbnail_path):
                    return f"Thumbnail exists in cache: {thumbnail_path}"
            except FileNotFoundError:
                pass  # Proceed to generate the thumbnail if files are missing

        # Generate thumbnail
        with Image.open(image_path) as img:
            # Create the output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Remove alpha channel or palette if necessary
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Create thumbnail
            img.thumbnail(size)

            # Save thumbnail
            ext = os.path.splitext(base_name)[1].lower()
            save_format = "JPEG" if ext in [".jpg", ".jpeg"] else "PNG"
            img.save(thumbnail_path, save_format)

            # Update cache
            valid_cache[thumbnail_path] = image_path
            return f"Thumbnail created: {thumbnail_path}"

    except Exception as e:
        return f"Error processing {image_path}: {e}"



def process_images(image_paths, output_dir, size=(720, 720)):
    """
    Processes a list of images to generate thumbnails using multiprocessing.
    Args:
        image_paths (list): List of image file paths.
        output_dir (str): Directory to save the thumbnails.
        size (tuple): Size of the thumbnails (width, height).
    """

    # Load the cache
    valid_cache = load_cache()

   # Clean the cache
    clean_cache(valid_cache)

    # Use multiprocessing with a shared cache manager
    with Manager() as manager:
        shared_cache = manager.dict(valid_cache)
        task_data = [(image_path, output_dir, size, shared_cache) for image_path in image_paths]

        with Pool(cpu_count()) as pool:
            results = pool.map(generate_thumbnail, task_data)

        valid_cache.update(shared_cache)
        save_cache(valid_cache)

    #debug
    # for result in results:
    #     print(result)


def clean_cache(cache):
    """
    Clean up the cache by removing entries for images or thumbnails that no longer exist.
    """
    to_remove = []

    for thumbnail_path, image_path in cache.items():
        if not os.path.exists(image_path) or not os.path.exists(thumbnail_path):
            # Mark cache entry for removal
            to_remove.append(thumbnail_path)
            # Delete the thumbnail if it exists
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
                print(f"Deleted thumbnail: {thumbnail_path}")

    # Remove invalid entries from the cache
    for thumbnail_path in to_remove:
        del cache[thumbnail_path]

    print(f"Cache cleaned. {len(to_remove)} entries removed.")


#  check if a file is a valid image
def is_image(file_path):
    try:
        with Image.open(file_path):
            return True
    except Exception:
        return False


# Main fucntion to call from the gui 
def ligma(wallpappers_dir):
    """
    source dir will be from file selector
    """
    source_dir = wallpappers_dir
    image_paths = [
        os.path.abspath(os.path.join(source_dir, file))
        for file in os.listdir(source_dir)
        if is_image(os.path.join(source_dir, file))
    ]
    
    #thumbnails
    output_dir = os.path.join(os.path.dirname(__file__),'thumbnails')

    # Generate thumbnails
    process_images(image_paths, output_dir)


if __name__ == "__main__":
    print('ligma is the main function')
