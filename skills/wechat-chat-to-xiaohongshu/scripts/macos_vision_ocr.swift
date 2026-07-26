import AppKit
import Foundation
import Vision

struct OCRLine {
    let pageIndex: Int
    let filename: String
    let x: Double
    let y: Double
    let width: Double
    let height: Double
    let confidence: Float
    let text: String
}

func cgImage(from path: String) -> CGImage? {
    guard let image = NSImage(contentsOfFile: path) else { return nil }
    var rect = NSRect(origin: .zero, size: image.size)
    return image.cgImage(forProposedRect: &rect, context: nil, hints: nil)
}

func tsvEscape(_ text: String) -> String {
    text.replacingOccurrences(of: "\t", with: " ")
        .replacingOccurrences(of: "\n", with: " ")
        .trimmingCharacters(in: .whitespacesAndNewlines)
}

func sideHint(x: Double, width: Double) -> String {
    let center = x + width / 2.0
    if center < 0.44 { return "left" }
    if center > 0.56 { return "right" }
    return "center"
}

func recognize(path: String, pageIndex: Int) throws -> [OCRLine] {
    guard let image = cgImage(from: path) else {
        throw NSError(domain: "macos_vision_ocr", code: 1, userInfo: [
            NSLocalizedDescriptionKey: "Cannot open image: \(path)"
        ])
    }

    let filename = URL(fileURLWithPath: path).lastPathComponent
    var lines: [OCRLine] = []
    let request = VNRecognizeTextRequest { request, error in
        if let error = error {
            fputs("OCR error for \(path): \(error)\n", stderr)
            return
        }
        let observations = request.results as? [VNRecognizedTextObservation] ?? []
        for observation in observations {
            guard let candidate = observation.topCandidates(1).first else { continue }
            let box = observation.boundingBox
            let text = tsvEscape(candidate.string)
            guard !text.isEmpty else { continue }
            lines.append(OCRLine(
                pageIndex: pageIndex,
                filename: filename,
                x: Double(box.minX),
                y: Double(box.minY),
                width: Double(box.width),
                height: Double(box.height),
                confidence: candidate.confidence,
                text: text
            ))
        }
    }

    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    request.recognitionLanguages = ["zh-Hans", "zh-Hant", "en-US"]
    if #available(macOS 13.0, *) {
        request.automaticallyDetectsLanguage = true
    }

    let handler = VNImageRequestHandler(cgImage: image, options: [:])
    try handler.perform([request])
    return lines.sorted {
        if abs($0.y - $1.y) > 0.012 {
            return $0.y > $1.y
        }
        return $0.x < $1.x
    }
}

let paths = Array(CommandLine.arguments.dropFirst())
if paths.isEmpty {
    fputs("usage: swift macos_vision_ocr.swift image1 [image2 ...]\n", stderr)
    exit(2)
}

print("page_index\tfilename\ty\tx\twidth\theight\tconfidence\tside_hint\ttext")
for (index, path) in paths.enumerated() {
    do {
        for line in try recognize(path: path, pageIndex: index + 1) {
            print(String(
                format: "%d\t%@\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%@\t%@",
                line.pageIndex,
                line.filename,
                line.y,
                line.x,
                line.width,
                line.height,
                line.confidence,
                sideHint(x: line.x, width: line.width),
                line.text
            ))
        }
    } catch {
        fputs("\(error)\n", stderr)
    }
}
