import os
import sys
from pathlib import Path
from markitdown import StreamInfo
from markitdown.converters import DocxConverter, PdfConverter

def convert_docx_to_markdown(file_path):
    try:
        converter = DocxConverter()
        stream_info = StreamInfo(local_path=str(file_path), filename=file_path.name, extension='.docx')
        with open(file_path, 'rb') as f:
            result = converter.convert(f, stream_info)
        return result.text_content if result else None
    except Exception as e:
        print(f"Error converting DOCX {file_path.name}: {e}")
        return None

def convert_pdf_to_markdown(file_path):
    try:
        converter = PdfConverter()
        stream_info = StreamInfo(local_path=str(file_path), filename=file_path.name, extension='.pdf')
        with open(file_path, 'rb') as f:
            result = converter.convert(f, stream_info)
        return result.text_content if result else None
    except Exception as e:
        print(f"Error converting PDF {file_path.name}: {e}")
        return None

def main():
    source_dir = Path(r"H:\github\md\123")
    target_dir = Path(r"H:\github\md\125")
    
    if not source_dir.exists():
        print(f"Source directory not found: {source_dir}")
        return
    
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
    
    files = list(source_dir.glob("*.*"))
    total_files = len(files)
    converted_count = 0
    skipped_count = 0
    failed_count = 0
    already_exists_count = 0
    
    print(f"Found {total_files} files in {source_dir}")
    
    for i, file_path in enumerate(files, 1):
        ext = file_path.suffix.lower()
        if ext not in ['.docx', '.pdf']:
            skipped_count += 1
            continue
        
        md_filename = file_path.stem + '.md'
        md_path = target_dir / md_filename
        
        if md_path.exists():
            already_exists_count += 1
            print(f"Processing ({i}/{total_files}): {file_path.name} - already exists, skipping")
            continue
            
        print(f"Processing ({i}/{total_files}): {file_path.name}")
        
        if ext == '.docx':
            md_content = convert_docx_to_markdown(file_path)
        else:
            md_content = convert_pdf_to_markdown(file_path)
        
        if md_content:
            try:
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                converted_count += 1
                print(f"  -> Converted to {md_filename}")
            except Exception as e:
                print(f"  -> Failed to write file: {e}")
                failed_count += 1
        else:
            failed_count += 1
            print(f"  -> Failed to convert")
    
    print(f"\nConversion complete!")
    print(f"Total files: {total_files}")
    print(f"Already exists: {already_exists_count}")
    print(f"Converted in this run: {converted_count}")
    print(f"Failed: {failed_count}")
    print(f"Skipped (non-docx/pdf): {skipped_count}")

if __name__ == "__main__":
    main()