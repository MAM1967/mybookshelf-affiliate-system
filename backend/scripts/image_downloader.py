#!/usr/bin/env python3
"""
Image Download and Conversion Script for MyBookshelf Affiliate System
"""

import requests
import base64
import os
import sys
from pathlib import Path

def download_and_convert_image(url, book_title=""):
    """
    Download an image from URL and convert to base64 data URL
    
    Args:
        url (str): The image URL to download
        book_title (str): Optional book title for naming/reference
        
    Returns:
        str: Base64 data URL or None if failed
    """
    try:
        print(f"Downloading image from: {url}")
        
        # Download the image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Get content type
        content_type = response.headers.get('content-type', 'image/jpeg')
        if not content_type.startswith('image/'):
            print(f"Warning: Content type is {content_type}, not an image")
            content_type = 'image/jpeg'  # Default fallback
        
        # Convert to base64
        image_data = base64.b64encode(response.content).decode('utf-8')
        data_url = f"data:{content_type};base64,{image_data}"
        
        print(f"✅ Successfully converted image for '{book_title}'")
        print(f"   Size: {len(response.content)} bytes")
        print(f"   Type: {content_type}")
        
        return data_url
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading image: {e}")
        return None
    except Exception as e:
        print(f"❌ Error converting image: {e}")
        return None

def save_image_locally(url, filename):
    """
    Download and save image locally for inspection
    
    Args:
        url (str): The image URL
        filename (str): Local filename to save as
        
    Returns:
        bool: True if successful
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Create images directory if it doesn't exist
        images_dir = Path('downloaded_images')
        images_dir.mkdir(exist_ok=True)
        
        # Save the image
        filepath = images_dir / filename
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Image saved locally as: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving image locally: {e}")
        return False

def interactive_mode():
    """
    Interactive mode for downloading and approving images
    """
    print("🖼️  MyBookshelf Image Download & Conversion Tool")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Download and convert image URL to base64")
        print("2. Download image locally for preview")
        print("3. Batch convert multiple URLs")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            url = input("Enter image URL: ").strip()
            if not url:
                print("❌ No URL provided")
                continue
                
            book_title = input("Enter book title (optional): ").strip()
            
            data_url = download_and_convert_image(url, book_title)
            if data_url:
                print("\n" + "="*50)
                print("Base64 Data URL (ready for database):")
                print("="*50)
                print(data_url[:100] + "..." if len(data_url) > 100 else data_url)
                print("="*50)
                
                # Offer to save to file
                save_choice = input("\nSave to file? (y/n): ").strip().lower()
                if save_choice == 'y':
                    filename = f"{book_title.replace(' ', '_').lower()}_base64.txt" if book_title else "image_base64.txt"
                    with open(filename, 'w') as f:
                        f.write(data_url)
                    print(f"✅ Saved to {filename}")
        
        elif choice == '2':
            url = input("Enter image URL: ").strip()
            if not url:
                print("❌ No URL provided")
                continue
                
            filename = input("Enter filename (e.g., book_cover.jpg): ").strip()
            if not filename:
                filename = "preview_image.jpg"
                
            save_image_locally(url, filename)
        
        elif choice == '3':
            print("\nBatch Mode - Enter image URLs (one per line, empty line to finish):")
            urls = []
            while True:
                url = input().strip()
                if not url:
                    break
                urls.append(url)
            
            if not urls:
                print("❌ No URLs provided")
                continue
            
            print(f"\nProcessing {len(urls)} URLs...")
            results = []
            
            for i, url in enumerate(urls, 1):
                print(f"\n--- Processing {i}/{len(urls)} ---")
                book_title = input(f"Book title for {url}: ").strip()
                
                data_url = download_and_convert_image(url, book_title)
                if data_url:
                    results.append({
                        'title': book_title,
                        'url': url,
                        'data_url': data_url
                    })
            
            if results:
                print(f"\n✅ Successfully processed {len(results)} images")
                
                # Save batch results
                batch_filename = "batch_images_base64.txt"
                with open(batch_filename, 'w') as f:
                    for result in results:
                        f.write(f"Title: {result['title']}\n")
                        f.write(f"Original URL: {result['url']}\n")
                        f.write(f"Base64 Data URL: {result['data_url']}\n")
                        f.write("-" * 80 + "\n\n")
                
                print(f"✅ Batch results saved to {batch_filename}")
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-4.")

def main():
    """
    Main function - can be called with command line args or interactively
    """
    if len(sys.argv) > 1:
        # Command line mode
        url = sys.argv[1]
        book_title = sys.argv[2] if len(sys.argv) > 2 else ""
        
        data_url = download_and_convert_image(url, book_title)
        if data_url:
            print(f"\nBase64 Data URL:\n{data_url}")
        else:
            sys.exit(1)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main() 