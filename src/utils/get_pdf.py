from fpdf import FPDF
import re

class CustomPDF(FPDF):
    def header(self):
        # Empty header
        pass

    def footer(self):
        # Empty footer
        pass

    def add_line_break_image(self, image_path):
        # Get current page width
        page_width = self.w
        
        # Set image width to be 1/3 of page width
        image_width = page_width / 3
        
        # Calculate x position to center the image
        x_pos = (page_width - image_width) / 2
        
        # Add the image
        current_y = self.get_y()
        self.image(image_path, x=x_pos, y=current_y, w=image_width)
        
        # Move y position below the image (assuming image height is proportional)
        self.ln(10)  # Adjust this value based on your image height

def parse_chapter(chapter_text):
    lines = chapter_text.strip().split("\n", 1)
    title_line = lines[0]
    content = lines[1].strip() if len(lines) > 1 else ""

    match = re.match(r"(Chapter \d+):\s(.+)", title_line)
    if match:
        chapter_number = match.group(1)
        chapter_title = match.group(2)
        return {
            "chapter_number": chapter_number,
            "chapter_title": chapter_title,
            "content": content,
        }
    return None

def create_pdf(output_path, story_title, story_theme, generated_chapters):

    pdf = CustomPDF()

    line_break_image_path = "/Users/pranav/Documents/Projects/fic-book/src/assets/line_break.png"
    
    # First page with title and theme
    pdf.add_page()
    
    # Calculate vertical position for title (around 1/3 of the page)
    title_y = pdf.h * 0.45
    
    # Add title with larger font
    pdf.set_font("Times", 'B', size=45)
    pdf.set_text_color(100, 0, 0)
    pdf.set_y(title_y)
    story_title = story_title.encode('latin-1', errors='ignore').decode('latin-1')
    pdf.cell(0, 10, txt=story_title, ln=1, align='C')

    pdf.ln(5)
    
    # Add theme with smaller font, slightly below title
    pdf.set_font("Times", size=14)
    pdf.set_text_color(0, 0, 0)
    story_theme = story_theme.encode('latin-1', errors='ignore').decode('latin-1')
    pdf.cell(0, 10, txt=story_theme, ln=1, align='C')
    
    # Process chapters
    for chapter in generated_chapters:
        parsed_chapter = parse_chapter(chapter)
        if parsed_chapter:
            pdf.add_page()

            # Add line break image between chapter number and title
            pdf.add_line_break_image(line_break_image_path)
            
            # Add chapter number centered at top with larger font
            pdf.set_font("Times", 'B', size=25)
            pdf.set_text_color(0, 0, 0)
            chapter_number = parsed_chapter["chapter_number"].encode('latin-1', errors='ignore').decode('latin-1')
            pdf.cell(0, 10, txt=chapter_number, ln=1, align='C')
            
            # Add chapter title centered below chapter number
            pdf.set_font("Times", 'B', size=24)
            pdf.set_text_color(100, 0, 0)
            chapter_title = parsed_chapter["chapter_title"].encode('latin-1', errors='ignore').decode('latin-1')
            pdf.cell(0, 10, txt=chapter_title, ln=1, align='C')
            
            # Add some space before content
            pdf.ln(10)
            
            # Add chapter content
            pdf.set_font("Times", size=12)
            pdf.set_text_color(0, 0, 0)
            content = parsed_chapter["content"].encode('latin-1', errors='ignore').decode('latin-1')
            pdf.multi_cell(0, 10, txt=content)
    
    pdf.output(output_path)