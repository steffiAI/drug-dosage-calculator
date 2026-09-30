"""
PDF Export Module for Drug Concentration Calculator.

Generates clean, print-optimized PDF reports for calculation protocols.
"""

import os
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT


class PDFExporter:
    """
    Generate clean, print-optimized PDF reports for calculation protocols.

    Parameters
    ----------
    output_dir : str, default="exports"
        Directory to save exported PDFs.
    """

    def __init__(self, output_dir: str = "exports") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def export_calculation(
        self,
        calculation_type: str,
        drug_name: str,
        inputs: dict,
        results: dict,
        solvent: str = "",
        timestamp: Optional[str] = None,
        filepath: Optional[Path] = None
    ) -> Path:
        """
        Export a single calculation to PDF.

        Parameters
        ----------
        calculation_type : str
            "Stock from Powder" or "Working from Stock"
        drug_name : str
            Name of the drug/compound
        inputs : dict
            Input parameters for the calculation
        results : dict
            Calculation results
        solvent : str, optional
            Solvent used
        timestamp : str, optional
            Calculation timestamp
        filepath : Path, optional
            Custom filepath for the PDF. If None, a default name is generated.

        Returns
        -------
        Path
            Path to the generated PDF file
        """
        # Use custom filepath or generate default
        if filepath is None:
            timestamp_str = timestamp or datetime.now().isoformat()
            date_str = timestamp_str.split('T')[0]
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in drug_name)
            filename = f"{date_str}_{safe_name}_{calculation_type.replace(' ', '_')}.pdf"
            filepath = self.output_dir / filename

        # Create PDF
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )

        # Build content
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
        )

        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.black,
            spaceAfter=6,
            spaceBefore=6,
        )

        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=16,
        )

        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=8,
            spaceBefore=12,
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
        )

        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#999999'),
        )

        # Top header line
        timestamp_str = timestamp or datetime.now().isoformat()
        date_str = timestamp_str.split('T')[0]

        header_data = [[
            Paragraph("Drug Concentration Calculator", header_style),
            Paragraph(f"Date: {date_str}", header_style),
        ]]
        header_table = Table(header_data, colWidths=[4.5*inch, 2*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.1*inch))

        # Separator line
        line_table = Table([['']], colWidths=[6.5*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#CCCCCC')),
        ]))
        story.append(line_table)
        story.append(Spacer(1, 0.2*inch))

        # Title
        if calculation_type == "Stock from Powder":
            story.append(Paragraph("STOCK SOLUTION PREPARATION PROTOCOL", title_style))
        else:
            story.append(Paragraph("WORKING SOLUTION PREPARATION PROTOCOL", title_style))

        story.append(Paragraph(f"Drug: {drug_name}", subtitle_style))

        # Compound information section
        story.append(Paragraph("COMPOUND INFORMATION", section_style))

        if calculation_type == "Stock from Powder":
            self._add_stock_info(story, inputs, solvent, body_style)
        else:
            self._add_dilution_info(story, inputs, results, solvent, body_style)

        story.append(Spacer(1, 0.1*inch))

        # Preparation protocol section
        story.append(Paragraph("PREPARATION PROTOCOL", section_style))

        if calculation_type == "Stock from Powder":
            self._add_stock_protocol(story, inputs, results, solvent, body_style)
        else:
            self._add_dilution_protocol(story, inputs, results, solvent, body_style)

        # Footer
        story.append(Spacer(1, 0.4*inch))
        line_table2 = Table([['']], colWidths=[6.5*inch])
        line_table2.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#CCCCCC')),
        ]))
        story.append(line_table2)
        story.append(Spacer(1, 0.1*inch))

        story.append(Paragraph(
            "Generated by Drug Concentration Calculator v3.1.0",
            footer_style
        ))
        story.append(Paragraph(
            "github.com/steffiAI/drug-dosage-calculator",
            footer_style
        ))

        # Build PDF
        doc.build(story)
        return filepath

    def _add_stock_info(self, story, inputs: dict, solvent: str, body_style) -> None:
        """Add stock solution compound information."""
        from formatters import format_number

        info_data = [
            ["Molecular Weight", f"{format_number(inputs.get('molecular_weight', 0))} g/mol"],
            ["Target Concentration",
             f"{format_number(inputs.get('target_concentration', 0))} {inputs.get('concentration_unit', '?')}"],
            ["Target Volume",
             f"{format_number(inputs.get('target_volume', 0))} {inputs.get('volume_unit', '?')}"],
            ["Solvent", solvent or "Not specified"],
        ]

        info_table = Table(info_data, colWidths=[2*inch, 4.5*inch])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(info_table)

    def _add_dilution_info(self, story, inputs: dict, results: dict, solvent: str, body_style) -> None:
        """Add dilution compound information."""
        from formatters import format_number

        info_data = [
            ["Stock Concentration",
             f"{format_number(inputs.get('stock_concentration', 0))} {inputs.get('stock_concentration_unit', '?')}"],
            ["Target Concentration",
             f"{format_number(inputs.get('target_concentration', 0))} {inputs.get('target_concentration_unit', '?')}"],
            ["Target Volume",
             f"{format_number(inputs.get('target_volume', 0))} {inputs.get('volume_unit', '?')}"],
            ["Dilution Factor", f"{format_number(results.get('dilution_factor', 0))}x"],
            ["Solvent", solvent or "Not specified"],
        ]

        info_table = Table(info_data, colWidths=[2*inch, 4.5*inch])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(info_table)

    def _add_stock_protocol(self, story, inputs: dict, results: dict, solvent: str, body_style) -> None:
        """Add stock solution preparation protocol."""
        from formatters import format_number, format_result_with_unit

        protocol_data = [
            [Paragraph("<b>1.</b>", body_style),
             Paragraph(f"WEIGH {format_result_with_unit(results.get('mass_mg', 0), 'mg')} of compound", body_style)],
            [Paragraph("<b>2.</b>", body_style),
             Paragraph(f"DISSOLVE in {format_number(inputs.get('target_volume', 0))} "
                      f"{inputs.get('volume_unit', '?')} {solvent or 'solvent'}", body_style)],
        ]

        protocol_table = Table(protocol_data, colWidths=[0.4*inch, 6.1*inch])
        protocol_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(protocol_table)

    def _add_dilution_protocol(self, story, inputs: dict, results: dict, solvent: str, body_style) -> None:
        """Add dilution preparation protocol."""
        from formatters import format_result_with_unit, convert_to_readable_unit

        vol_unit = inputs.get('volume_unit', '?')
        stock_vol, stock_vol_unit = convert_to_readable_unit(results.get('stock_volume', 0), vol_unit)
        solvent_vol, solvent_vol_unit = convert_to_readable_unit(results.get('solvent_volume', 0), vol_unit)

        protocol_data = [
            [Paragraph("<b>1.</b>", body_style),
             Paragraph(f"TAKE {format_result_with_unit(stock_vol, stock_vol_unit)} of stock solution", body_style)],
            [Paragraph("<b>2.</b>", body_style),
             Paragraph(f"ADD {format_result_with_unit(solvent_vol, solvent_vol_unit)} of {solvent or 'solvent'}", body_style)],
        ]

        protocol_table = Table(protocol_data, colWidths=[0.4*inch, 6.1*inch])
        protocol_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(protocol_table)

    def export_multiple_calculations(self, calculations: list, filepath: Path) -> Path:
        """
        Export multiple calculations to a single PDF.

        Parameters
        ----------
        calculations : list of dict
            List of calculation records from history.
        filepath : Path
            Path for the output PDF file.

        Returns
        -------
        Path
            Path to the generated PDF file.
        """
        # Create PDF
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )

        story = []
        styles = getSampleStyleSheet()

        # Styles
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
        )

        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.black,
            spaceAfter=6,
            spaceBefore=6,
        )

        protocol_title_style = ParagraphStyle(
            'ProtocolTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.black,
            spaceAfter=6,
            spaceBefore=16,
        )

        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=16,
        )

        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=8,
            spaceBefore=12,
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
        )

        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#999999'),
        )

        # Top header
        date_str = datetime.now().strftime("%Y-%m-%d")
        header_data = [[
            Paragraph("Drug Concentration Calculator", header_style),
            Paragraph(f"Date: {date_str}", header_style),
        ]]
        header_table = Table(header_data, colWidths=[4.5*inch, 2*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.1*inch))

        # Separator line
        line_table = Table([['']], colWidths=[6.5*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#CCCCCC')),
        ]))
        story.append(line_table)
        story.append(Spacer(1, 0.2*inch))

        # Main title
        story.append(Paragraph(f"PREPARATION PROTOCOLS ({len(calculations)} Calculations)", title_style))
        story.append(Spacer(1, 0.2*inch))

        # Add each calculation
        for idx, calc in enumerate(calculations, 1):
            calc_type = calc["calculation_type"]
            drug_name = calc["drug_name"]
            inputs = calc["inputs"]
            results = calc["results"]
            solvent = calc.get("solvent", "Not specified")

            # Protocol number and title
            if calc_type == "Stock from Powder":
                protocol_title = f"Protocol {idx}: Stock Solution - {drug_name}"
            else:
                protocol_title = f"Protocol {idx}: Working Solution - {drug_name}"

            story.append(Paragraph(protocol_title, protocol_title_style))

            # Information
            story.append(Paragraph("COMPOUND INFORMATION", section_style))

            if calc_type == "Stock from Powder":
                self._add_stock_info(story, inputs, solvent, body_style)
            else:
                self._add_dilution_info(story, inputs, results, solvent, body_style)

            story.append(Spacer(1, 0.1*inch))

            # Protocol steps
            story.append(Paragraph("PREPARATION PROTOCOL", section_style))

            if calc_type == "Stock from Powder":
                self._add_stock_protocol(story, inputs, results, solvent, body_style)
            else:
                self._add_dilution_protocol(story, inputs, results, solvent, body_style)

            # Add separator between protocols (except after the last one)
            if idx < len(calculations):
                story.append(Spacer(1, 0.3*inch))
                separator = Table([['']], colWidths=[6.5*inch])
                separator.setStyle(TableStyle([
                    ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#EEEEEE')),
                ]))
                story.append(separator)

        # Footer
        story.append(Spacer(1, 0.4*inch))
        line_table2 = Table([['']], colWidths=[6.5*inch])
        line_table2.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#CCCCCC')),
        ]))
        story.append(line_table2)
        story.append(Spacer(1, 0.1*inch))

        story.append(Paragraph(
            "Generated by Drug Concentration Calculator v3.1.0",
            footer_style
        ))
        story.append(Paragraph(
            "github.com/steffiAI/drug-dosage-calculator",
            footer_style
        ))

        # Build PDF
        doc.build(story)
        return filepath

    def open_pdf(self, filepath: Path) -> None:
        """
        Open a PDF file with the system default viewer.

        Parameters
        ----------
        filepath : Path
            Path to the PDF file to open.
        """
        try:
            if platform.system() == 'Windows':
                os.startfile(str(filepath))
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(filepath)], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', str(filepath)], check=True)
        except Exception:
            pass  # Silently fail if we can't open the PDF
