import os
import django
import sys

# Setup Django
sys.path.append('c:\\Users\\zfhin\\OneDrive\\project\\CampusClubDiscovery\\campushub')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campushub.settings')
django.setup()

from core.models import Post, PostImage

def link_post_images():
    print("Starting post image linking...")
    posts_dir = 'c:\\Users\\zfhin\\OneDrive\\project\\CampusClubDiscovery\\campushub\\media\\posts'
    
    if not os.path.exists(posts_dir):
        print(f"Error: Directory {posts_dir} does not exist.")
        return

    all_files = os.listdir(posts_dir)
    print(f"Total files in posts_dir: {len(all_files)}")
    
    linked_count = 0
    
    # Files are like: shortcode_index.jpg (e.g. B-37WqRpj4f_0.jpg)
    for fname in all_files:
        if not fname.endswith(('.jpg', '.png', '.jpeg')):
            continue
            
        # Parse short_code and order
        parts = fname.rsplit('_', 1)
        if len(parts) != 2:
            continue
            
        short_code = parts[0]
        try:
            order_part = parts[1].split('.')[0]
            order = int(order_part)
        except ValueError:
            continue
            
        # Try to find the post
        try:
            # Note: short_code in DB might match the filename prefix
            post = Post.objects.filter(short_code=short_code).first()
            if not post:
                # Try searching by ID if short_code doesn't match? 
                # But usually Instagram short_codes are used
                continue
                
            # Check if this image is already linked
            # We want to avoid duplicates if possible, but creating them is safer for restoration
            relative_path = os.path.join('posts', fname)
            
            # Create PostImage record
            # We use get_or_create to avoid duplicates if the script is run twice
            pi, created = PostImage.objects.get_or_create(
                post=post,
                order=order,
                defaults={'image': relative_path}
            )
            
            if created:
                # print(f"LINKED: Post {short_code} Image {order} -> {relative_path}")
                linked_count += 1
            else:
                # Update if already exists but maybe path was different?
                pi.image = relative_path
                pi.save()
                
        except Exception as e:
            print(f"Error processing {fname}: {e}")

    print(f"\nDone! Linked {linked_count} new post images.")
    print(f"Total PostImage records now: {PostImage.objects.count()}")

if __name__ == '__main__':
    link_post_images()
