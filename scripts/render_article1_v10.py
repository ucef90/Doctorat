"""Render the V10 status report with automatically generated research figures."""
from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
import matplotlib

ROOT=Path(__file__).resolve().parents[1]


def markup(text):
    text=escape(text.replace('–','-').replace('—','-').replace('‑','-'))
    text=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<link href="\2" color="#087f8c">\1</link>',text)
    return re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',text).replace('`','')


def main():
    font=Path(matplotlib.get_data_path())/'fonts/ttf'
    for name,file in [('DV','DejaVuSans.ttf'),('DV-Bold','DejaVuSans-Bold.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(font/file)))
    pdfmetrics.registerFontFamily('DV',normal='DV',bold='DV-Bold',italic='DV',boldItalic='DV-Bold')
    body=ParagraphStyle('Body',fontName='DV',fontSize=9.3,leading=14,spaceAfter=8)
    h2=ParagraphStyle('H2',parent=body,fontName='DV-Bold',fontSize=14,leading=19,spaceBefore=13,
                      spaceAfter=8,textColor=colors.HexColor('#17354D'),keepWithNext=True)
    h3=ParagraphStyle('H3',parent=h2,fontSize=11,leading=15)
    title=ParagraphStyle('Title',parent=h2,fontSize=26,leading=32,spaceAfter=16)
    cell=ParagraphStyle('Cell',parent=body,fontSize=7.3,leading=10,spaceAfter=0,wordWrap='CJK')
    small=ParagraphStyle('Small',parent=body,fontSize=8,leading=12,textColor=colors.HexColor('#566979'))
    width=A4[0]-84
    out=ROOT/'output/pdf/ARTICLE1_STATUS_V10.pdf';out.parent.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(out),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=40,bottomMargin=42,
                          title='Article 1 - Bilan scientifique V10',author='Youssef EL MOUTEE')
    story=[Paragraph('RECOA-PINN / ARTICLE 1',small),Spacer(1,12),
           Paragraph('Bilan scientifique V10',title),
           Paragraph('Référence indépendante, données difficiles et sensibilité aux budgets',body),
           Paragraph('Youssef EL MOUTEE | 5 septembre 2026 | Version de recherche',small),Spacer(1,12)]
    lines=(ROOT/'ARTICLE1_STATUS_V10.md').read_text().splitlines()
    i=0
    while i<len(lines):
        line=lines[i]
        if not line.strip() or line.startswith('# ') or line.startswith('**Youssef'):
            i+=1;continue
        if line.startswith('|'):
            data=[]
            while i<len(lines) and lines[i].startswith('|'):
                line=lines[i]
                if not re.match(r'^\|[-: |]+\|$',line):
                    data.append([Paragraph(markup(v.strip()),cell) for v in line.strip('|').split('|')])
                i+=1
            n=len(data[0]); widths=[width/n]*n
            if n==2:widths=[width*.34,width*.66]
            if n==6:widths=[width*f for f in (.16,.15,.19,.16,.23,.11)]
            t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DDEBF0')),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F4F7F9')]),
                ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),
                ('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),6),
                ('BOTTOMPADDING',(0,0),(-1,-1),6)]))
            story.extend([t,Spacer(1,10)]);continue
        if line.startswith('## '):story.append(Paragraph(markup(line[3:]),h2));i+=1;continue
        if line.startswith('### '):story.append(Paragraph(markup(line[4:]),h3));i+=1;continue
        para=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|')):
            para.append(lines[i]);i+=1
        story.append(Paragraph(markup(' '.join(para)),body))
    for file,heading,caption in [
        ('outputs/reference_v10_analysis/reference_validation.png','Référence Burgers',
         'Comparaison des solutions numériques et des maxima de 50 modèles figés. Le second panneau change aussi la grille d’évaluation.'),
        ('outputs/robustness_v10_verified/l2_by_seed.png','Ablations sous données difficiles',
         'Chaque point représente un germe ; le trait noir marque la médiane. Les tables d’inférence corrigent la multiplicité des contrastes.'),
        ('outputs/budget_v10_analysis/l2_by_seed.png','Ablations à budget de pas doublé',
         'Les budgets sont égaux entre bras d’une même EDP. Ils ne sont pas des budgets de temps égaux.')]:
        story.extend([PageBreak(),Paragraph(heading,h2),Spacer(1,12)])
        im=Image(str(ROOT/file));im.drawHeight=im.imageHeight*width/im.imageWidth;im.drawWidth=width
        story.extend([im,Spacer(1,12),Paragraph(markup(caption),body)])
    def footer(canvas,doc):
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#CBD8E0'))
        canvas.line(42,31,A4[0]-42,31);canvas.setFont('DV',7)
        canvas.setFillColor(colors.HexColor('#566979'))
        canvas.drawString(42,20,'Article 1 | V10 | Résultats exploratoires')
        canvas.drawRightString(A4[0]-42,20,str(doc.page));canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print(out)


if __name__=='__main__':main()
