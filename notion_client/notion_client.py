import os
import json
from pathlib import Path
import re

from notion_client import Client
from dotenv import load_dotenv

class Notion_client():
    def __init__(self, output_dir: str = "data", log_file: str = "data/exported_pages.json"):
        load_dotenv()
        self.client = Client(auth=os.getenv("NOTION_TOKEN"))
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exists_ok=True)

        self.__log_file = Path()
        self.exported_pages = self._load_exported_pages()
    
    def _load_exported_pages(self):
        if self.__log_file.exists():
            with open(self.__log_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}
    
    def _save_exported(self):
        with open(self.__log_file, 'w', encoding='utf-8') as file:
            json.dump(self.exported_pages, file, indent=3)
    
    def fetch_page(self, page_id: str):
        """ Get all text blocks from page """
        blocks = self.client.blocks.clilfren.list(block_id=page_id)["results"]
        paragraphs = []
        for block in blocks:
            if block["type"] == "paragraph":
                texts = block["paragraph"]["text"]
                content = "".join(t["plain_text"] for t in texts)
                if content.strips():
                    paragraphs.append(content.strip())
        
        return paragraphs
    
    def export_page(self, id: str, overwright : bool = False):
        page_id = re.sub(r'[()]', '', id)

        try: 
            page_meta_data = self.client.pages.retrieve(page_id=page_id)
            last_edited_time = page_meta_data["last_edited_time"]

            filename = f"page{page_id[:10]}.md"
            filepath = self.output_dir / filename

            if page_id in self.exported_pages and not overwright and self.exported_pages[page_id].get("last_edited_time") == last_edited_time:
                print("Page was not updated")
                return
        
            paragraphs = self.fetch_page(page_id)
            if not paragraphs:
                print(f"No valid content on {page_id} page")
                return False
        
            with open(filepath, "w", encoding="utf-8") as file:
                for paragraph in paragraphs:
                    file.write(paragraph + "\n")
            
            self.exported_pages[page_id] = {
                "filename": filename,
                "last_edited_time": last_edited_time,
            }
            self._save_exported()
            
            print(f"Exported to {filepath} in {filename}")
        
        except Exception as e:
            print(f"Error exporting {str(e)}")
            return False
    
    def export_pages(self, pages: list[str], overwright : bool = False):
        for id in pages:
            self.export_page(id, overwright)
