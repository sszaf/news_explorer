from fpdf import FPDF

BOLDED = 'B'
ITALICS = 'I'
HEADER_FONT_SIZE = 12
FOOTER_FONT_SIZE = 8
BOTTOM_MARGIN = -15
FOOTER_CENTERING = 'C'
AUTO_WIDTH = 0
CELL_HEIGHT = 10
ORIGINAL_TITLE_INFO = 'ORIGINAL TITLE: '
HEADER_GAP = 10
EMPTY_STRING = ''

class PDF(FPDF):
    def __init__(self,header_text=EMPTY_STRING):
        super().__init__()
        self.header_text = ORIGINAL_TITLE_INFO + header_text
        self.set_auto_page_break(auto=True)
        self.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)

    def header(self):
        self.set_font('DejaVu', '', HEADER_FONT_SIZE)
        self.multi_cell(AUTO_WIDTH,CELL_HEIGHT,self.header_text)
        self.line(self.l_margin, self.t_margin+20, self.w - self.r_margin, self.t_margin+20)
        self.ln(HEADER_GAP)

    def footer(self):
        self.set_font('DejaVu', '', FOOTER_FONT_SIZE)
        self.set_y(BOTTOM_MARGIN)
        self.cell(AUTO_WIDTH, CELL_HEIGHT, f'Page {self.page_no()}',align=FOOTER_CENTERING)
       