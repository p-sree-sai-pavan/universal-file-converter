# universal_file_converter.py

import os
import subprocess
from typing import List, Dict, Tuple

# ---- Conversion Plugins Registry ----

class ConversionPlugin:
    input_formats: List[str] = []
    output_formats: List[str] = []
    name: str = ""

    def convert(self, infile, outfile):
        raise NotImplementedError()

# Example Plugin: FFmpeg Audio/Video
class FFmpegConverter(ConversionPlugin):
    input_formats = ['mp3', 'wav', 'ogg', 'mp4', 'avi', 'mov', 'flac', 'aac']
    output_formats = ['mp3', 'wav', 'ogg', 'mp4', 'avi', 'mov', 'flac', 'aac']
    name = "ffmpeg"

    def convert(self, infile, outfile):
        subprocess.run(['ffmpeg', '-y', '-i', infile, outfile], check=True)

# Example Plugin: ImageMagick
class ImageMagickConverter(ConversionPlugin):
    input_formats = ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif']
    output_formats = ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif']
    name = "imagemagick"

    def convert(self, infile, outfile):
        subprocess.run(['convert', infile, outfile], check=True)

# Example Plugin: LibreOffice for Documents (via unoconv)
class UnoconvConverter(ConversionPlugin):
    input_formats = ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'ods', 'odp', 'pdf']
    output_formats = ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'ods', 'odp', 'pdf']
    name = "unoconv"

    def convert(self, infile, outfile):
        subprocess.run(['unoconv', '-f', outfile.split('.')[-1], '-o', outfile, infile], check=True)

# Expand plugins as needed (e.g., Calibre for ebooks, 7z for archives...)

# ---- Core Conversion Graph Engine ----

class ConversionRegistry:
    def __init__(self):
        self.plugins: List[ConversionPlugin] = [FFmpegConverter(), ImageMagickConverter(), UnoconvConverter()]
        self.graph: Dict[str, Dict[str, ConversionPlugin]] = {}
        self._build_graph()

    def _build_graph(self):
        for plugin in self.plugins:
            for i in plugin.input_formats:
                for o in plugin.output_formats:
                    self.graph.setdefault(i, {})
                    self.graph[i][o] = plugin

    def find_path(self, input_fmt, output_fmt, path=None, seen=None):
        if path is None: path = [input_fmt]
        if seen is None: seen = set()
        if input_fmt == output_fmt:
            return path
        seen.add(input_fmt)
        neighbors = self.graph.get(input_fmt, {})
        for fmt in neighbors:
            if fmt in seen: continue
            sub_path = self.find_path(fmt, output_fmt, path + [fmt], seen)
            if sub_path:
                return sub_path
        return None

    def convert(self, infile, outfile):
        ext_in = infile.split('.')[-1].lower()
        ext_out = outfile.split('.')[-1].lower()
        path = self.find_path(ext_in, ext_out)
        if not path:
            raise Exception(f"No conversion path found from {ext_in} to {ext_out}")
        temp_files = [infile]
        for i in range(1, len(path)):
            next_ext = path[i]
            new_out = outfile if i == len(path) - 1 else f"tmp_{i}.{next_ext}"
            plugin = self.graph[path[i-1]][next_ext]
            plugin.convert(temp_files[-1], new_out)
            temp_files.append(new_out)
        # Cleanup intermediates
        for f in temp_files[1:-1]:
            os.remove(f)
        print(f"Conversion complete: {outfile}")

# ---- CLI Entrypoint ----

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python universal_file_converter.py input_file output_file")
        exit(1)
    reg = ConversionRegistry()
    reg.convert(sys.argv[1], sys.argv[2])
