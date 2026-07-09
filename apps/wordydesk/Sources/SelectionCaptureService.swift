import AppKit
import Foundation

struct SelectionCaptureService {
    func captureSelection() async throws -> String {
        let pasteboard = NSPasteboard.general
        let previousString = pasteboard.string(forType: .string)
        let previousChangeCount = pasteboard.changeCount

        try simulateCopyShortcut()
        try await Task.sleep(for: .milliseconds(220))

        guard pasteboard.changeCount != previousChangeCount,
              let copiedText = pasteboard.string(forType: .string),
              copiedText.rangeOfCharacter(from: .letters) != nil else {
            if let previousString,
               previousString.rangeOfCharacter(from: .letters) != nil,
               previousChangeCount == 0 {
                return previousString
            }
            throw AppError.clipboardReadFailed
        }

        return copiedText
    }

    private func simulateCopyShortcut() throws {
        guard let source = CGEventSource(stateID: .combinedSessionState) else {
            throw AppError.clipboardReadFailed
        }

        let keyDown = CGEvent(keyboardEventSource: source, virtualKey: 8, keyDown: true)
        let keyUp = CGEvent(keyboardEventSource: source, virtualKey: 8, keyDown: false)
        keyDown?.flags = .maskCommand
        keyUp?.flags = .maskCommand
        keyDown?.post(tap: .cghidEventTap)
        keyUp?.post(tap: .cghidEventTap)
    }
}
