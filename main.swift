import AppKit
import Foundation

struct FormatError: LocalizedError {
    let errorDescription: String?
    init(_ message: String) { errorDescription = message }
}

struct Bytes {
    let data: Data

    init(_ url: URL) throws {
        data = try Data(contentsOf: url, options: .mappedIfSafe)
    }

    func byte(_ offset: Int) throws -> Int {
        guard data.indices.contains(offset) else {
            throw FormatError("Unexpected end of file at byte \(offset).")
        }
        return Int(data[offset])
    }

    func littleEndian(_ offset: Int, size: Int) throws -> Int {
        var value = 0
        for index in 0..<size {
            value |= try byte(offset + index) << (index * 8)
        }
        return value
    }
}

func inspectArchive(_ archive: Bytes) throws {
    let sectorSize = 2048
    guard try archive.littleEndian(0, size: 4) == sectorSize else {
        throw FormatError("Expected the AVATAR archive's first resource at byte 2048.")
    }

    var previous = sectorSize
    var rows = ["entry,offset,padded_length"]
    for index in 1..<(sectorSize / 4) {
        let end = try archive.littleEndian(index * 4, size: 4)
        guard end > previous, end <= archive.data.count, end.isMultiple(of: sectorSize) else {
            throw FormatError("Invalid archive offset at index \(index).")
        }
        rows.append("\(index - 1),\(previous),\(end - previous)")
        if end == archive.data.count {
            print(rows.joined(separator: "\n"))
            return
        }
        previous = end
    }
    throw FormatError("Missing archive end offset.")
}

struct PackedPixels {
    let page: Bytes
    let start: Int
    let wordSize: Int
    let wordCount: Int
    var position = 0

    mutating func word() throws -> Int {
        guard position < wordCount else { throw FormatError("Truncated sprite data.") }
        let bitOffset = position * wordSize
        position += 1
        let offset = start + bitOffset / 8
        let first = try page.byte(offset)
        let shift = 8 - bitOffset % 8 - wordSize
        let mask = (1 << wordSize) - 1
        if shift >= 0 { return (first >> shift) & mask }
        return try ((first << -shift) | (page.byte(offset + 1) >> (8 + shift))) & mask
    }

    mutating func count() throws -> Int {
        let first = try word()
        if first != 0 { return first }
        let second = try (word() << 4) | word()
        if second != 0 { return second }
        return try (word() << 8) | (word() << 4) | word()
    }

    mutating func decode(pixelCount: Int) throws -> [Int] {
        var pixels: [Int] = []
        while pixels.count < pixelCount {
            let first = try count()
            if first != 1 {
                let repeats = first == 2 ? try count() : 1
                for index in 0..<repeats where pixels.count < pixelCount {
                    let length = index == 0 && first != 2 ? first : try count()
                    let value = try word()
                    pixels.append(contentsOf: repeatElement(value, count: min(length, pixelCount - pixels.count)))
                }
            }
            if pixels.count < pixelCount {
                let length = try count()
                for _ in 0..<min(length, pixelCount - pixels.count) {
                    pixels.append(try word())
                }
            }
        }
        return pixels
    }
}

struct DOSFrame {
    let bitmap: NSBitmapImageRep
    let pageName: String
    let index: Int
    let hotspotX: Int
    let hotspotY: Int
}

func readFrame(root: URL, actor: Int, slot: Int, frame: Int) throws -> DOSFrame {
    let crit = root.appendingPathComponent("CRIT")
    let associations = try Bytes(crit.appendingPathComponent("ASSOC.ANM"))
    let index = 256 + (actor - 64) * 2
    let animation = try associations.byte(index)
    let palette = try associations.byte(index + 1)
    guard animation < 32 else { throw FormatError("Actor has no animation association.") }

    for pageNumber in 0...1 {
        let name = String(format: "CR%02oPAGE.N%02o", animation, pageNumber)
        let url = crit.appendingPathComponent(name)
        guard FileManager.default.fileExists(atPath: url.path) else { continue }
        let page = try Bytes(url)
        let baseSlot = try page.byte(0)
        let slotCount = try page.byte(1)
        guard (baseSlot..<(baseSlot + slotCount)).contains(slot) else { continue }
        let segmentCount = try page.byte(2 + slotCount)
        let segment = try page.byte(2 + slot - baseSlot)
        guard segment < segmentCount else { continue }
        let frameIndex = try page.byte(3 + slotCount + segment * 8 + frame)
        guard frameIndex != 255 else { throw FormatError("Animation slot has no frame \(frame).") }
        let paletteHeader = 3 + slotCount + segmentCount * 8
        let paletteCount = try page.byte(paletteHeader)
        guard palette < paletteCount else { throw FormatError("Invalid auxiliary palette.") }
        let offsetHeader = paletteHeader + 1 + paletteCount * 32
        guard frameIndex < (try page.byte(offsetHeader)) else {
            throw FormatError("Invalid frame index \(frameIndex).")
        }
        let offset = try page.littleEndian(offsetHeader + 2 + frameIndex * 2, size: 2)
        let width = try page.byte(offset)
        let height = try page.byte(offset + 1)
        let compression = try page.byte(offset + 4)
        guard width > 0, height > 0, [6, 8].contains(compression) else {
            throw FormatError("Unsupported sprite frame format.")
        }
        let wordCount = try page.littleEndian(offset + 5, size: 2)
        var packed = PackedPixels(page: page, start: offset + 7,
                                  wordSize: compression == 6 ? 5 : 4, wordCount: wordCount)
        let pixels = try packed.decode(pixelCount: width * height)
        let colors = try Bytes(root.appendingPathComponent("DATA/PALS.DAT"))
        guard let bitmap = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: width, pixelsHigh: height,
                                           bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                                           colorSpaceName: .deviceRGB, bitmapFormat: .alphaNonpremultiplied,
                                           bytesPerRow: width * 4, bitsPerPixel: 32),
              let destination = bitmap.bitmapData else {
            throw FormatError("Could not allocate PNG pixels.")
        }
        for (index, atom) in pixels.enumerated() {
            let color = try page.byte(paletteHeader + 1 + palette * 32 + atom)
            for channel in 0..<3 {
                destination[index * 4 + channel] = UInt8(clamping: try colors.byte(color * 3 + channel) * 255 / 63)
            }
            destination[index * 4 + 3] = color == 0 ? 0 : 255
        }
        return try DOSFrame(bitmap: bitmap, pageName: name, index: frameIndex,
                            hotspotX: page.byte(offset + 2), hotspotY: page.byte(offset + 3))
    }
    throw FormatError("Animation slot is absent from both CRIT pages.")
}

func exportFrame(root: URL, actor: Int, slot: Int, frame: Int, output: URL) throws {
    let result = try readFrame(root: root, actor: actor, slot: slot, frame: frame)
    let bitmap = result.bitmap
    guard let png = bitmap.representation(using: .png, properties: [:]) else {
        throw FormatError("Could not encode PNG.")
    }
    try png.write(to: output, options: .withoutOverwriting)
    print("\(result.pageName), frame \(result.index), \(bitmap.pixelsWide)×\(bitmap.pixelsHigh), hotspot (\(result.hotspotX), \(result.hotspotY))")
}

func exportLanugoAtlas(root: URL, directory: URL) throws {
    let width = 256
    let height = 192
    let sequence = try (32...39).flatMap { slot in
        try (0..<4).map { phase in
            (slot, phase, try readFrame(root: root, actor: 70, slot: slot, frame: phase))
        }
    }
    var uniqueFrames: [Int: DOSFrame] = [:]
    for (_, _, frame) in sequence {
        uniqueFrames[frame.index] = frame
    }
    let orderedFrames = uniqueFrames.values.sorted {
        if $0.bitmap.pixelsHigh != $1.bitmap.pixelsHigh {
            return $0.bitmap.pixelsHigh > $1.bitmap.pixelsHigh
        }
        return $0.index < $1.index
    }
    var pixels = [UInt16](repeating: 0, count: width * height)
    var positions: [Int: (u: Int, v: Int)] = [:]
    var u = 0
    var v = 0
    var shelfHeight = 0
    for frame in orderedFrames {
        let bitmap = frame.bitmap
        let frameWidth = bitmap.pixelsWide
        let frameHeight = bitmap.pixelsHigh
        if u + frameWidth > width {
            u = 0
            v += shelfHeight
            shelfHeight = 0
        }
        guard frameWidth <= width, v + frameHeight <= height, let rgba = bitmap.bitmapData else {
            throw FormatError("Lanugo idle sequence exceeds the atlas bounds.")
        }
        for y in 0..<frameHeight {
            for x in 0..<frameWidth {
                let color = y * bitmap.bytesPerRow + x * 4
                guard rgba[color + 3] != 0 else { continue }
                let red = UInt16(rgba[color]) >> 3
                let green = UInt16(rgba[color + 1]) >> 3
                let blue = UInt16(rgba[color + 2]) >> 3
                let value = red | green << 5 | blue << 10
                pixels[(v + y) * width + u + x] = value == 0 ? 0x8000 : value
            }
        }
        positions[frame.index] = (u, v)
        u += frameWidth
        shelfHeight = max(shelfHeight, frameHeight)
    }
    var rows = ["slot,phase,u,v,width,height,hotspot_x,hotspot_y"]
    for (slot, phase, frame) in sequence {
        guard let position = positions[frame.index] else {
            throw FormatError("Lanugo frame is missing from the packed atlas.")
        }
        rows.append("\(slot),\(phase),\(position.u),\(position.v),\(frame.bitmap.pixelsWide),\(frame.bitmap.pixelsHigh),\(frame.hotspotX),\(frame.hotspotY)")
    }

    // A 16-bit TIM with no CLUT. VRAM placement is relative until allocated by the renderer.
    let imageBytes = UInt32(12 + pixels.count * 2)
    var data = Data()
    for word: UInt32 in [0x10, 2, imageBytes] {
        withUnsafeBytes(of: word.littleEndian) { data.append(contentsOf: $0) }
    }
    for halfword: UInt16 in [0, 0, UInt16(width), UInt16(height)] {
        withUnsafeBytes(of: halfword.littleEndian) { data.append(contentsOf: $0) }
    }
    for pixel in pixels {
        withUnsafeBytes(of: pixel.littleEndian) { data.append(contentsOf: $0) }
    }

    try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: false)
    try data.write(to: directory.appendingPathComponent("lanugo-idle.tim"), options: .withoutOverwriting)
    try Data((rows.joined(separator: "\n") + "\n").utf8)
        .write(to: directory.appendingPathComponent("lanugo-idle.csv"), options: .withoutOverwriting)
}

let arguments = Array(CommandLine.arguments.dropFirst())
do {
    switch arguments.first {
    case "inspect-psx" where arguments.count == 2:
        try inspectArchive(Bytes(URL(fileURLWithPath: arguments[1])))
    case "export-lanugo-tim" where arguments.count == 3:
        try exportLanugoAtlas(root: URL(fileURLWithPath: arguments[1]),
                              directory: URL(fileURLWithPath: arguments[2]))
    case "export-dos" where arguments.count == 6:
        guard let actor = Int(arguments[2]), (64...127).contains(actor),
              let slot = Int(arguments[3]), (0...255).contains(slot),
              let frame = Int(arguments[4]), (0...7).contains(frame) else {
            throw FormatError("Use decimal actor ID 64–127, slot 0–255, and frame 0–7.")
        }
        try exportFrame(root: URL(fileURLWithPath: arguments[1]), actor: actor, slot: slot,
                        frame: frame, output: URL(fileURLWithPath: arguments[5]))
    default:
        throw FormatError("""
        Usage
          UnderworldVisuals inspect-psx AVATAR
          UnderworldVisuals export-lanugo-tim DOS_ROOT NEW_OUTPUT_DIRECTORY
          UnderworldVisuals export-dos DOS_ROOT ACTOR_ID SLOT FRAME OUTPUT.png
        """)
    }
} catch {
    FileHandle.standardError.write(Data((error.localizedDescription + "\n").utf8))
    exit(1)
}
