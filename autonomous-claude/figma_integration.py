#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figma Integration for Autonomous Claude
קורא עיצובים מ-Figma ומייצר קוד אוטומטית
"""
import requests
import json
from typing import Dict, List, Optional
import os


class FigmaClient:
    """Client for Figma API integration."""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize Figma client.

        Args:
            token: Figma Personal Access Token (or use FIGMA_TOKEN env var)
        """
        self.token = token or os.getenv('FIGMA_TOKEN')
        if not self.token:
            raise ValueError("Figma token required. Set FIGMA_TOKEN or pass token parameter.")

        self.base_url = "https://api.figma.com/v1"
        self.headers = {
            "X-Figma-Token": self.token,
            "Content-Type": "application/json"
        }

    def get_file(self, file_key: str) -> Dict:
        """
        Get Figma file data.

        Args:
            file_key: Figma file key from URL (figma.com/file/FILE_KEY/...)

        Returns:
            Complete file data including all frames, components, styles
        """
        url = f"{self.base_url}/files/{file_key}"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Figma API error: {response.status_code} - {response.text}")

        return response.json()

    def get_file_styles(self, file_key: str) -> Dict:
        """Get all styles (colors, text styles) from file."""
        url = f"{self.base_url}/files/{file_key}/styles"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Figma API error: {response.status_code}")

        return response.json()

    def get_images(self, file_key: str, node_ids: List[str], scale: float = 2.0, format: str = 'png') -> Dict:
        """
        Export images from Figma.

        Args:
            file_key: Figma file key
            node_ids: List of node IDs to export
            scale: Export scale (1.0, 2.0, etc.)
            format: Image format (png, jpg, svg, pdf)

        Returns:
            Dict with node_id -> image_url mapping
        """
        url = f"{self.base_url}/images/{file_key}"
        params = {
            'ids': ','.join(node_ids),
            'scale': scale,
            'format': format
        }

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Figma API error: {response.status_code}")

        return response.json()

    def extract_colors(self, file_data: Dict) -> List[Dict]:
        """Extract all colors from design."""
        colors = []

        def traverse(node):
            # Check fills
            if 'fills' in node:
                for fill in node['fills']:
                    if fill.get('type') == 'SOLID' and 'color' in fill:
                        color = fill['color']
                        rgb = f"rgb({int(color['r']*255)}, {int(color['g']*255)}, {int(color['b']*255)})"
                        colors.append({
                            'name': node.get('name', 'Unnamed'),
                            'rgb': rgb,
                            'rgba': color
                        })

            # Traverse children
            if 'children' in node:
                for child in node['children']:
                    traverse(child)

        if 'document' in file_data:
            traverse(file_data['document'])

        return colors

    def extract_text_styles(self, file_data: Dict) -> List[Dict]:
        """Extract all text styles."""
        text_styles = []

        def traverse(node):
            if node.get('type') == 'TEXT':
                style = node.get('style', {})
                text_styles.append({
                    'name': node.get('name', 'Unnamed'),
                    'fontFamily': style.get('fontFamily', 'Arial'),
                    'fontSize': style.get('fontSize', 16),
                    'fontWeight': style.get('fontWeight', 400),
                    'lineHeight': style.get('lineHeightPx', 24),
                    'letterSpacing': style.get('letterSpacing', 0)
                })

            if 'children' in node:
                for child in node['children']:
                    traverse(child)

        if 'document' in file_data:
            traverse(file_data['document'])

        return text_styles

    def extract_components(self, file_data: Dict) -> List[Dict]:
        """Extract all components."""
        components = []

        def traverse(node):
            if node.get('type') == 'COMPONENT':
                components.append({
                    'id': node.get('id'),
                    'name': node.get('name'),
                    'type': node.get('type'),
                    'absoluteBoundingBox': node.get('absoluteBoundingBox')
                })

            if 'children' in node:
                for child in node['children']:
                    traverse(child)

        if 'document' in file_data:
            traverse(file_data['document'])

        return components

    def generate_tailwind_config(self, file_data: Dict) -> str:
        """Generate Tailwind CSS config from Figma design."""
        colors = self.extract_colors(file_data)
        text_styles = self.extract_text_styles(file_data)

        # Build color palette
        color_config = {}
        for i, color in enumerate(colors[:10]):  # Limit to top 10 colors
            color_name = f"figma-{i+1}"
            color_config[color_name] = color['rgb']

        # Build font sizes
        font_sizes = {}
        for i, style in enumerate(text_styles[:10]):
            size_name = f"figma-{i+1}"
            font_sizes[size_name] = f"{style['fontSize']}px"

        config = f"""
// Tailwind Config from Figma
module.exports = {{
  theme: {{
    extend: {{
      colors: {json.dumps(color_config, indent=8)},
      fontSize: {json.dumps(font_sizes, indent=8)}
    }}
  }}
}}
"""
        return config

    def generate_css_variables(self, file_data: Dict) -> str:
        """Generate CSS variables from Figma design."""
        colors = self.extract_colors(file_data)
        text_styles = self.extract_text_styles(file_data)

        css = ":root {\n"

        # Colors
        css += "  /* Colors from Figma */\n"
        for i, color in enumerate(colors[:10]):
            css += f"  --figma-color-{i+1}: {color['rgb']};\n"

        # Typography
        css += "\n  /* Typography from Figma */\n"
        for i, style in enumerate(text_styles[:10]):
            css += f"  --figma-font-{i+1}: {style['fontSize']}px;\n"

        css += "}\n"
        return css


class FigmaToHTML:
    """Convert Figma designs to HTML/Tailwind."""

    def __init__(self, client: FigmaClient):
        self.client = client

    def frame_to_html(self, node: Dict, indent: int = 0) -> str:
        """Convert Figma frame to HTML."""
        node_type = node.get('type')
        name = node.get('name', 'Unnamed')

        html = ""
        indent_str = "  " * indent

        if node_type == 'FRAME':
            html += f'{indent_str}<div class="frame" data-name="{name}">\n'

            if 'children' in node:
                for child in node['children']:
                    html += self.frame_to_html(child, indent + 1)

            html += f'{indent_str}</div>\n'

        elif node_type == 'TEXT':
            style = node.get('style', {})
            text = node.get('characters', '')
            font_size = style.get('fontSize', 16)
            font_weight = style.get('fontWeight', 400)

            html += f'{indent_str}<p class="text-[{font_size}px] font-[{font_weight}]">{text}</p>\n'

        elif node_type == 'RECTANGLE':
            bg_color = self._get_fill_color(node)
            width = node.get('absoluteBoundingBox', {}).get('width', 'auto')
            height = node.get('absoluteBoundingBox', {}).get('height', 'auto')

            html += f'{indent_str}<div class="w-[{width}px] h-[{height}px]" style="background: {bg_color}"></div>\n'

        return html

    def _get_fill_color(self, node: Dict) -> str:
        """Get fill color from node."""
        fills = node.get('fills', [])
        if fills and fills[0].get('type') == 'SOLID':
            color = fills[0]['color']
            return f"rgb({int(color['r']*255)}, {int(color['g']*255)}, {int(color['b']*255)})"
        return 'transparent'


# Example usage
if __name__ == '__main__':
    print("=" * 70)
    print("🎨 Figma Integration for Autonomous Claude")
    print("=" * 70)
    print()

    # Check for token
    if not os.getenv('FIGMA_TOKEN'):
        print("⚠️  FIGMA_TOKEN not set")
        print("   Get token from: https://www.figma.com/settings")
        print("   Then: export FIGMA_TOKEN='your-token'")
        print()
        print("Usage:")
        print("  1. Set FIGMA_TOKEN environment variable")
        print("  2. Get file key from Figma URL")
        print("  3. Run: python figma_integration.py")
        print()
    else:
        print("✅ FIGMA_TOKEN found!")
        print()
        print("Ready to import designs from Figma! 🚀")
