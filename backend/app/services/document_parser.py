import os
import re
from docx import Document
from PyPDF2 import PdfReader
from PIL import Image

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

class DocumentParser:
    def __init__(self):
        self.ocr_path = None

    def set_tesseract_path(self, path):
        self.ocr_path = path
        if self.ocr_path:
            pytesseract.pytesseract.tesseract_cmd = self.ocr_path

    def parse(self, file_path: str, file_ext: str, doc_type: str = "auto") -> str:
        if file_ext == "docx":
            return self._parse_docx(file_path)
        elif file_ext == "pdf":
            return self._parse_pdf(file_path)
        elif file_ext in ["txt", "md"]:
            return self._parse_text(file_path)
        elif file_ext in ["png", "jpg", "jpeg", "webp"]:
            return self._parse_image(file_path)
        else:
            return self._parse_text(file_path)

    def _parse_docx(self, file_path: str) -> str:
        doc = Document(file_path)
        content = []
        for para in doc.paragraphs:
            if para.text.strip():
                content.append(para.text)
        return "\n".join(content)

    def _parse_pdf(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        content = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                content.append(text)
        return "\n".join(content)

    def _parse_text(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _parse_image(self, file_path: str) -> str:
        ocr_text = self._try_ocr(file_path)
        
        if ocr_text and ocr_text.strip():
            return ocr_text
        
        visual_features = self._analyze_image_features(file_path)
        
        content = "【图片分析结果】\n\n"
        content += "识别到的UI元素:\n"
        
        for feature in visual_features:
            content += f"- {feature}\n"
        
        content += "\n【基于界面特征的需求描述】\n"
        content += self._generate_requirements_from_features(visual_features)
        
        return content

    def _try_ocr(self, file_path: str) -> str:
        if not OCR_AVAILABLE:
            return ""
        
        try:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img, lang="chi_sim")
            return text if text.strip() else ""
        except Exception as e:
            return ""

    def _analyze_image_features(self, file_path: str) -> list:
        features = []
        
        try:
            img = Image.open(file_path)
            width, height = img.size
            
            features.append(f"图片尺寸: {width}x{height}")
            
            grayscale = img.convert('L')
            brightness = self._calculate_brightness(grayscale)
            features.append(f"平均亮度: {brightness:.1f}")
            
            edge_density = self._detect_edges(grayscale)
            features.append(f"边缘密度: {edge_density:.2f}")
            
            text_regions = self._detect_text_regions(img)
            if text_regions:
                features.append(f"检测到{len(text_regions)}个文本区域")
            
            buttons = self._detect_buttons(img)
            if buttons:
                features.append(f"检测到{len(buttons)}个按钮/可点击元素")
            
            input_fields = self._detect_input_fields(img)
            if input_fields:
                features.append(f"检测到{len(input_fields)}个输入框")
            
            tables = self._detect_tables(grayscale)
            if tables:
                features.append(f"检测到{len(tables)}个表格")
            
        except Exception as e:
            features.append(f"图片分析异常: {str(e)}")
        
        return features

    def _calculate_brightness(self, grayscale: Image) -> float:
        pixels = list(grayscale.getdata())
        return sum(pixels) / len(pixels)

    def _detect_edges(self, grayscale: Image) -> float:
        width, height = grayscale.size
        pixels = list(grayscale.getdata())
        edge_count = 0
        total_pixels = width * height
        
        for i in range(height - 1):
            for j in range(width - 1):
                idx = i * width + j
                current = pixels[idx]
                right = pixels[idx + 1]
                down = pixels[idx + width]
                
                if abs(current - right) > 30:
                    edge_count += 1
                if abs(current - down) > 30:
                    edge_count += 1
        
        return edge_count / total_pixels

    def _detect_text_regions(self, img: Image) -> list:
        regions = []
        width, height = img.size
        grayscale = img.convert('L')
        
        for i in range(0, height, 30):
            for j in range(0, width, 100):
                box = (j, i, min(j + 100, width), min(i + 30, height))
                region = grayscale.crop(box)
                pixels = list(region.getdata())
                if pixels:
                    avg = sum(pixels) / len(pixels)
                    variance = sum((p - avg) ** 2 for p in pixels) / len(pixels)
                    if variance > 400:
                        regions.append((j, i))
        
        return regions[:5]

    def _detect_buttons(self, img: Image) -> list:
        buttons = []
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        width, height = img.size
        pixels = list(img.getdata())
        
        blue_pixels = sum(1 for r, g, b in pixels if b > 150 and r < 150 and g < 150)
        green_pixels = sum(1 for r, g, b in pixels if g > 150 and r < 150 and b < 150)
        orange_pixels = sum(1 for r, g, b in pixels if r > 180 and g > 100 and b < 100)
        
        if blue_pixels > 500:
            buttons.append("蓝色按钮")
        if green_pixels > 500:
            buttons.append("绿色按钮")
        if orange_pixels > 500:
            buttons.append("橙色按钮")
        
        return buttons

    def _detect_input_fields(self, img: Image) -> list:
        inputs = []
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        width, height = img.size
        pixels = list(img.getdata())
        
        light_pixels = sum(1 for r, g, b in pixels if r > 230 and g > 230 and b > 230)
        gray_pixels = sum(1 for r, g, b in pixels if 200 < r < 240 and 200 < g < 240 and 200 < b < 240)
        
        if light_pixels > width * height * 0.1:
            inputs.append("浅色背景区域")
        if gray_pixels > width * height * 0.05:
            inputs.append("灰色输入框")
        
        return inputs

    def _detect_tables(self, grayscale: Image) -> list:
        tables = []
        width, height = grayscale.size
        pixels = list(grayscale.getdata())
        
        vertical_edges = 0
        for j in range(width):
            for i in range(height - 1):
                idx = i * width + j
                if abs(pixels[idx] - pixels[idx + width]) > 20:
                    vertical_edges += 1
        
        horizontal_edges = 0
        for i in range(height):
            for j in range(width - 1):
                idx = i * width + j
                if abs(pixels[idx] - pixels[idx + 1]) > 20:
                    horizontal_edges += 1
        
        if vertical_edges > height * 2 and horizontal_edges > width * 2:
            tables.append(f"表格结构: 垂直边{vertical_edges}条, 水平边{horizontal_edges}条")
        
        return tables

    def _generate_requirements_from_features(self, features: list) -> str:
        has_buttons = any("按钮" in f for f in features)
        has_inputs = any("输入框" in f or "浅色" in f or "灰色" in f for f in features)
        has_tables = any("表格" in f for f in features)
        has_text = any("文本区域" in f for f in features)
        
        requirements = []
        
        if has_buttons and has_inputs:
            requirements.append("功能: 用户登录与认证 - 用户可以通过输入用户名和密码进行登录")
            requirements.append("功能: 数据查询 - 用户可以通过输入条件查询数据")
            requirements.append("功能: 数据提交 - 用户可以填写表单并提交数据")
        
        if has_tables:
            requirements.append("功能: 数据列表展示 - 系统以表格形式展示数据列表")
            requirements.append("功能: 数据分页 - 支持分页查看大量数据")
        
        if has_text:
            requirements.append("功能: 信息展示 - 系统展示关键信息和提示")
        
        requirements.append("功能: 界面导航 - 用户可以通过按钮和菜单进行页面导航")
        requirements.append("功能: 数据新增 - 用户可以新增数据记录")
        requirements.append("功能: 数据修改 - 用户可以修改已有数据")
        requirements.append("功能: 数据删除 - 用户可以删除数据记录")
        requirements.append("功能: 权限验证 - 系统验证用户访问权限")
        
        return "\n".join(requirements)

    def extract_features(self, content: str) -> dict:
        features = {
            "functions": self._extract_functions(content),
            "requirements": self._extract_requirements(content),
            "parameters": self._extract_parameters(content),
            "business_rules": self._extract_business_rules(content)
        }
        return features

    def _extract_functions(self, content: str) -> list:
        patterns = [
            r'功能[:：]\s*(.+?)(?=\n|$)',
            r'功能点[:：]\s*(.+?)(?=\n|$)',
            r'模块[:：]\s*(.+?)(?=\n|$)',
            r'接口[:：]\s*(.+?)(?=\n|$)',
            r'操作[:：]\s*(.+?)(?=\n|$)'
        ]
        functions = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            functions.extend([m.strip() for m in matches if m.strip()])
        return list(set(functions))

    def _extract_requirements(self, content: str) -> list:
        patterns = [
            r'需求[:：]\s*(.+?)(?=\n|$)',
            r'要求[:：]\s*(.+?)(?=\n|$)',
            r'必须[:：]\s*(.+?)(?=\n|$)',
            r'应该[:：]\s*(.+?)(?=\n|$)',
            r'需要[:：]\s*(.+?)(?=\n|$)'
        ]
        requirements = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            requirements.extend([m.strip() for m in matches if m.strip()])
        return list(set(requirements))

    def _extract_parameters(self, content: str) -> list:
        patterns = [
            r'参数[:：]\s*(.+?)(?=\n|$)',
            r'输入[:：]\s*(.+?)(?=\n|$)',
            r'输出[:：]\s*(.+?)(?=\n|$)',
            r'返回[:：]\s*(.+?)(?=\n|$)'
        ]
        parameters = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            parameters.extend([m.strip() for m in matches if m.strip()])
        return list(set(parameters))

    def _extract_business_rules(self, content: str) -> list:
        patterns = [
            r'规则[:：]\s*(.+?)(?=\n|$)',
            r'条件[:：]\s*(.+?)(?=\n|$)',
            r'逻辑[:：]\s*(.+?)(?=\n|$)',
            r'判断[:：]\s*(.+?)(?=\n|$)'
        ]
        rules = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            rules.extend([m.strip() for m in matches if m.strip()])
        return list(set(rules))