"""Render the measured French report with tables and scientific figures."""
import argparse
from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image


def markup(text):
    text=text.replace("–","-").replace("—","-").replace("‑","-")
    text=escape(text)
    text=re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",r'<link href="\2" color="#0072B2">\1</link>',text)
    text=re.sub(r"\*\*(.*?)\*\*",r"<b>\1</b>",text)
    return text.replace("`","")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report")
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    source=Path(args.report)
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    font_dir=Path(__import__("matplotlib").get_data_path())/"fonts"/"ttf"
    pdfmetrics.registerFont(TTFont("DejaVu",str(font_dir/"DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold",str(font_dir/"DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFontFamily("DejaVu",normal="DejaVu",bold="DejaVu-Bold",italic="DejaVu",boldItalic="DejaVu-Bold")
    styles=getSampleStyleSheet()
    body=ParagraphStyle("ReportBody",fontName="DejaVu",fontSize=9.4,leading=14,spaceAfter=7)
    h2=ParagraphStyle("ReportH2",parent=body,fontName="DejaVu-Bold",fontSize=15,leading=20,
                      textColor=colors.HexColor("#15334A"),spaceBefore=14,spaceAfter=8,keepWithNext=True)
    h3=ParagraphStyle("ReportH3",parent=h2,fontSize=11,leading=16,spaceBefore=10)
    cell=ParagraphStyle("Cell",parent=body,fontSize=7.7,leading=10.5,spaceAfter=0)
    code=ParagraphStyle("Code",parent=body,fontSize=7.4,leading=11,backColor=colors.HexColor("#F3F5F7"),wordWrap="CJK")
    title=ParagraphStyle("ReportTitle",parent=h2,fontSize=29,leading=36,spaceAfter=20)
    subtitle=ParagraphStyle("Subtitle",parent=body,fontSize=13,leading=20,textColor=colors.HexColor("#496376"))
    small=ParagraphStyle("Small",parent=body,fontSize=8,leading=12,textColor=colors.HexColor("#596579"))
    doc=SimpleDocTemplate(str(output),pagesize=A4,rightMargin=40,leftMargin=40,topMargin=42,bottomMargin=42,
                          title="Article 1 - Ablations vRBA : rapport experimental v0.9",author="Youssef EL MOUTEE")
    width=A4[0]-80
    story=[Spacer(1,45),Paragraph("ARTICLE 1 / CAHIER EXPÉRIMENTAL",small),Spacer(1,25),
           Paragraph("Comprendre les mécanismes<br/>de vRBA",title),
           Paragraph("Attention locale, équilibrage global et choix du potentiel",subtitle),Spacer(1,25),
           Paragraph("200 entraînements appariés<br/>4 équations - 10 germes - 5 variantes<br/>60 essais CPU complémentaires",subtitle),
           Spacer(1,35),Paragraph("Youssef EL MOUTEE",body),Paragraph("Rapport v0.9 - 5 septembre 2026",body),Spacer(1,30),
           Paragraph("Étude exploratoire reproductible. Les résultats, les absences de preuve et les limites "
                     "sont présentés ensemble. Ce document ne constitue pas une publication évaluée par les pairs.",body),PageBreak()]
    lines=source.read_text().splitlines()
    index=0
    in_code=False
    while index<len(lines):
        line=lines[index]
        if line.startswith("# "):
            index+=1
            continue
        if line.startswith("```"):
            in_code=not in_code
            index+=1
            continue
        if in_code:
            story.append(Paragraph(escape(line),code))
            index+=1
            continue
        if line.startswith("|"):
            rows=[]
            while index<len(lines) and lines[index].startswith("|"):
                raw=lines[index]
                if not re.match(r"^\|[-: |]+\|$",raw):
                    rows.append([Paragraph(markup(x.strip()),cell) for x in raw.strip("|").split("|")])
                index+=1
            n=len(rows[0])
            widths=[width/n]*n
            if n==6:
                widths=[width*x for x in (.11,.20,.13,.27,.12,.17)]
            table=Table(rows,colWidths=widths,repeatRows=1,hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E4EDF2")),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F6F8FA")]),
                ("VALIGN",(0,0),(-1,-1),"TOP"),
                ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
                ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
                ("LINEBELOW",(0,0),(-1,0),.6,colors.HexColor("#B6C6D2"))]))
            story.extend([table,Spacer(1,9)])
            continue
        if line.startswith("## "):
            story.append(Paragraph(markup(line[3:]),h2))
        elif line.startswith("### "):
            story.append(Paragraph(markup(line[4:]),h3))
        elif line.strip():
            story.append(Paragraph(markup(line),body))
        index+=1
    figures=[
        ("l2_by_seed.png","Figure 1. Variabilité de l'erreur globale",
         "Chaque point représente un germe. Le trait horizontal est la médiane. Les écarts entre problèmes "
         "reflètent aussi leurs architectures, budgets et solutions de référence distincts."),
        ("maximum_by_seed.png","Figure 2. Erreurs maximales sur grille",
         "Ces maxima discrets complètent L2 et rendent visibles les erreurs localisées. Ils ne sont pas "
         "des bornes continues certifiées."),
        ("paired_l2_effects.png","Figure 3. Effets appariés et incertitude",
         "Les barres sont des IC bootstrap marginaux à 95 %. La couleur bleue signale p Holm inférieur "
         "à 0,05 dans la famille L2. Les barres et les tests corrigés n'utilisent pas la même règle "
         "d'inférence : une barre excluant zéro peut rester grise."),
        ("burgers_error_maps.png","Figure 4. Localisation des erreurs de Burgers",
         "Médiane ponctuelle des erreurs absolues sur les dix germes, avec grille et référence affinées. "
         "Les couleurs partagent une même échelle. Une carte médiane n'est pas un modèle individuel."),
    ]
    for filename,heading,caption in figures:
        story.extend([PageBreak(),Paragraph(heading,h2),Spacer(1,12)])
        image=Image(str(source.parent/filename))
        image.drawHeight=image.imageHeight*width/image.imageWidth
        image.drawWidth=width
        story.extend([image,Spacer(1,16),Paragraph(caption,body)])
    def footer(canvas,doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D8E1E8"))
        canvas.line(40,32,A4[0]-40,32)
        canvas.setFont("DejaVu",7.2)
        canvas.setFillColor(colors.HexColor("#596579"))
        canvas.drawString(40,21,"ReCoA-PINN / Rapport expérimental v0.9")
        canvas.drawRightString(A4[0]-40,21,str(doc.page))
        canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print(output)


if __name__=="__main__":
    main()
