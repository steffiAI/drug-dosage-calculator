"""
PDF Export Module for Drug Concentration Calculator.

Generates professional PDF reports for calculation protocols.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class PDFExporter:
    """
    Generate professional PDF reports for calculation protocols.

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
        timestamp: Optional[str] = None
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

        Returns
        -------
        Path
            Path to the generated PDF file
        """
        # Generate filename
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
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#5CB8EC'),
            spaceAfter=6,
            alignment=TA_CENTER,
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#9AA0A6'),
            spaceAfter=20,
            alignment=TA_CENTER,
        )

        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#5CB8EC'),
            spaceAfter=10,
            spaceBefore=10,
        )

        # Header
        story.append(Paragraph("Drug Concentration Calculator", title_style))
        story.append(Paragraph(calculation_type, subtitle_style))
        story.append(Spacer(1, 0.2*inch))

        # Drug info section
        story.append(Paragraph("Compound Information", header_style))

        drug_data = [
            ["Drug Name:", drug_name],
            ["Date:", date_str],
            ["Solvent:", solvent or "Not specified"],
        ]

        drug_table = Table(drug_data, colWidths=[2*inch, 4.5*inch])
        drug_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#9AA0A6')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#FFFFFF')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2F2F2F')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(drug_table)
        story.append(Spacer(1, 0.3*inch))

        # Parameters and protocol sections based on type
        if calculation_type == "Stock from Powder":
            self._add_stock_protocol(story, inputs, results, header_style)
        else:
            self._add_dilution_protocol(story, inputs, results, header_style)

        # Footer
        story.append(Spacer(1, 0.4*inch))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2A2A2A')))
        story.append(Spacer(1, 0.1*inch))

        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#7D8287'),
            alignment=TA_CENTER,
        )
        story.append(Paragraph(
            "Generated by Drug Concentration Calculator v3.1.0 | "
            "github.com/steffiAI/drug-dosage-calculator",
            footer_style
        ))

        # Build PDF
        doc.build(story)
        return filepath

    def _add_stock_protocol(self, story, inputs: dict, results: dict, header_style) -> None:
        """Add stock solution protocol to PDF."""
        from formatters import format_number, format_result_with_unit

        # Parameters
        story.append(Paragraph("Parameters", header_style))

        params_data = [
            ["Molecular Weight:", f"{format_number(inputs.get('molecular_weight', 0))} g/mol"],
            ["Target Concentration:",
             f"{format_number(inputs.get('target_concentration', 0))} {inputs.get('concentration_unit', '?')}"],
            ["Target Volume:",
             f"{format_number(inputs.get('target_volume', 0))} {inputs.get('volume_unit', '?')}"],
        ]

        params_table = Table(params_data, colWidths=[2*inch, 4.5*inch])
        params_table.setStyle(self._get_table_style())
        story.append(params_table)
        story.append(Spacer(1, 0.3*inch))

        # Protocol
        story.append(Paragraph("Preparation Protocol", header_style))

        protocol_data = [
            ["Step 1:", f"WEIGH {format_result_with_unit(results.get('mass_mg', 0), 'mg')} of compound"],
            ["Step 2:",
             f"DISSOLVE in {format_number(inputs.get('target_volume', 0))} "
             f"{inputs.get('volume_unit', '?')} of solvent"],
        ]

        protocol_table = Table(protocol_data, colWidths=[1*inch, 5.5*inch])
        protocol_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 12),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#5CB8EC')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#FFFFFF')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#262626')),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2A2A2A')),
        ]))
        story.append(protocol_table)

    def _add_dilution_protocol(self, story, inputs: dict, results: dict, header_style) -> None:
        """Add dilution protocol to PDF."""
        from formatters import format_number, format_result_with_unit, convert_to_readable_unit

        # Parameters
        story.append(Paragraph("Parameters", header_style))

        params_data = [
            ["Stock Concentration:",
             f"{format_number(inputs.get('stock_concentration', 0))} {inputs.get('stock_concentration_unit', '?')}"],
            ["Target Concentration:",
             f"{format_number(inputs.get('target_concentration', 0))} {inputs.get('target_concentration_unit', '?')}"],
            ["Target Volume:",
             f"{format_number(inputs.get('target_volume', 0))} {inputs.get('volume_unit', '?')}"],
            ["Dilution Factor:", f"{format_number(results.get('dilution_factor', 0))}x"],
        ]

        params_table = Table(params_data, colWidths=[2*inch, 4.5*inch])
        params_table.setStyle(self._get_table_style())
        story.append(params_table)
        story.append(Spacer(1, 0.3*inch))

        # Protocol
        story.append(Paragraph("Dilution Protocol", header_style))

        vol_unit = inputs.get('volume_unit', '?')
        stock_vol, stock_vol_unit = convert_to_readable_unit(results.get('stock_volume', 0), vol_unit)
        solvent_vol, solvent_vol_unit = convert_to_readable_unit(results.get('solvent_volume', 0), vol_unit)

        protocol_data = [
            ["Step 1:", f"TAKE {format_result_with_unit(stock_vol, stock_vol_unit)} of stock solution"],
            ["Step 2:", f"ADD {format_result_with_unit(solvent_vol, solvent_vol_unit)} of solvent"],
        ]

        protocol_table = Table(protocol_data, colWidths=[1*inch, 5.5*inch])
        protocol_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 12),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#5CB8EC')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#FFFFFF')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#262626')),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2A2A2A')),
        ]))
        story.append(protocol_table)

    def _get_table_style(self) -> TableStyle:
        """Get standard table style for parameters."""
        return TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#9AA0A6')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#FFFFFF')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2F2F2F')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ])
