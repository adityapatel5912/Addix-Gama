"""
Module documentation.
"""

import logging
import re
import xml.sax.saxutils
from typing import Any, List

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from gama.schema import StateContext

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class MarkdownParser:
    """Base class for Markdown parsers."""

    def can_parse(self, line: str) -> bool:
        raise NotImplementedError

    def parse(self, line: str, styles: Any) -> Any:
        raise NotImplementedError


class HeaderParser(MarkdownParser):
    def can_parse(self, line: str) -> bool:
        return line.startswith("#")

    def parse(self, line: str, styles: Any) -> Any:
        match = re.match(r"^(#{1,6})\s+(.*)", line)
        if match:
            level = len(match.group(1))
            text = match.group(2)
            text = xml.sax.saxutils.escape(text)
            style_name = f"Heading{level}"
            style = styles[style_name] if style_name in styles else styles["Heading1"]
            return Paragraph(text, style)
        return None


class ListParser(MarkdownParser):
    def can_parse(self, line: str) -> bool:
        return bool(re.match(r"^[\-\*\+]\s+.*|^[0-9]+\.\s+.*", line))

    def parse(self, line: str, styles: Any) -> Any:
        match_ul = re.match(r"^[\-\*\+]\s+(.*)", line)
        if match_ul:
            text = xml.sax.saxutils.escape(match_ul.group(1))
            return ListItem(Paragraph(text, styles["Normal"]))

        match_ol = re.match(r"^[0-9]+\.\s+(.*)", line)
        if match_ol:
            text = xml.sax.saxutils.escape(match_ol.group(1))
            return ListItem(Paragraph(text, styles["Normal"]))

        return None


class BlockquoteParser(MarkdownParser):
    def can_parse(self, line: str) -> bool:
        return line.startswith(">")

    def parse(self, line: str, styles: Any) -> Any:
        match = re.match(r"^>\s+(.*)", line)
        if match:
            # Create a special style for blockquotes if it doesn't exist
            if "Blockquote" not in styles:
                styles.add(
                    ParagraphStyle(
                        name="Blockquote",
                        parent=styles["Normal"],
                        leftIndent=20,
                        rightIndent=20,
                        textColor=HexColor("#555555"),
                        fontName="Helvetica-Oblique",
                    )
                )
            text = xml.sax.saxutils.escape(match.group(1))
            return Paragraph(text, styles["Blockquote"])
        return None


class ParagraphParser(MarkdownParser):
    def can_parse(self, line: str) -> bool:
        return len(line.strip()) > 0

    def parse(self, line: str, styles: Any) -> Any:
        # Basic bold/italic inline handling
        # Escape XML entities before adding formatting tags
        line = xml.sax.saxutils.escape(line)
        # Bold
        line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
        line = re.sub(r"__(.*?)__", r"<b>\1</b>", line)
        # Italic
        line = re.sub(r"\*(.*?)\*", r"<i>\1</i>", line)
        line = re.sub(r"_(.*?)_", r"<i>\1</i>", line)
        # Code
        line = re.sub(r"`(.*?)`", r'<font name="Courier">\1</font>', line)
        return Paragraph(line, styles["Normal"])


class MarkdownToPDFConverter:
    def __init__(self, output_filename: str):
        self.output_filename = output_filename
        self.styles = getSampleStyleSheet()
        self.styles.add(
            ParagraphStyle(
                name="ReportTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                spaceAfter=20,
                textColor=HexColor("#2c3e50"),
            )
        )

        self.parsers = [
            HeaderParser(),
            ListParser(),
            BlockquoteParser(),
            ParagraphParser(),
        ]

    def _get_flowable(self, line: str) -> Any:
        for parser in self.parsers:
            if parser.can_parse(line):
                return parser.parse(line, self.styles)
        return None

    def convert(self, markdown_text: str):
        doc = SimpleDocTemplate(
            self.output_filename,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        story = []

        # Add a title
        story.append(
            Paragraph("Gama Audit Certification Report", self.styles["ReportTitle"])
        )
        story.append(Spacer(1, 0.25 * inch))

        # Remove emojis before converting as standard ReportLab fonts don't support them
        markdown_text = (
            markdown_text.replace("✅", "")
            .replace("🚨", "")
            .replace("📝", "")
            .replace("🛠️", "")
        )

        lines = markdown_text.split("\n")
        current_list_items = []
        is_ordered_list = False

        for line in lines:
            line = line.strip()
            if not line:
                if current_list_items:
                    list_type = "bullet" if not is_ordered_list else "1"
                    story.append(ListFlowable(current_list_items, bulletType=list_type))
                    current_list_items = []
                story.append(Spacer(1, 0.1 * inch))
                continue

            flowable = self._get_flowable(line)

            if isinstance(flowable, ListItem):
                if not current_list_items:
                    is_ordered_list = re.match(r"^[0-9]+\.", line) is not None
                current_list_items.append(flowable)
            else:
                if current_list_items:
                    list_type = "bullet" if not is_ordered_list else "1"
                    story.append(ListFlowable(current_list_items, bulletType=list_type))
                    current_list_items = []

                if flowable:
                    story.append(flowable)

        if current_list_items:
            list_type = "bullet" if not is_ordered_list else "1"
            story.append(ListFlowable(current_list_items, bulletType=list_type))

        doc.build(story)


def generate_audit_report(state_context: StateContext, output_path: str):
    """
    Generates a PDF audit report from a StateContext Pydantic model.
    """

    # We can still generate a markdown-like structure to feed into the existing converter,
    # or build the story directly. Since MarkdownToPDFConverter exists and handles
    # paragraph styles nicely, we will build a pristine markdown string from the Pydantic schema
    # to feed it.

    md_lines = []
    md_lines.append("# Certification Report")
    md_lines.append(f"**Overall Status:** {state_context.overall_status}")
    md_lines.append("")
    md_lines.append(f"**Success Rate:** {state_context.summary.success_rate * 100}%")
    md_lines.append(
        f"**Passed:** {state_context.summary.passed} / **Total:** {state_context.summary.total}"
    )
    md_lines.append("")

    if state_context.overall_status == "PASSED":
        md_lines.append("## All Systems Go")
        md_lines.append(
            "No failures detected in the target project. The codebase is currently fully operational and production-ready."
        )
    else:
        md_lines.append("## Findings")
        for err_info in state_context.aggregated_errors:
            md_lines.append(f"### Category: {err_info.evaluator}")
            for error in err_info.errors:
                md_lines.append(
                    f"- **{error.title}** ({error.severity}): {error.description}"
                )
                if error.file:
                    md_lines.append(f"  - File: `{error.file}` (Line: {error.line})")
                md_lines.append(f"  - Fix: {error.instructions}")
            md_lines.append("")

    converter = MarkdownToPDFConverter(output_path)
    converter.convert("\n".join(md_lines))
