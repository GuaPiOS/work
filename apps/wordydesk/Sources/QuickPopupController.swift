import AppKit
import SwiftUI

@MainActor
final class QuickPopupController {
    private var panel: NSPanel?
    private var hideTimer: Timer?
    private var trackingMonitor: Any?

    func show(
        entry: WordEntry,
        onSpeakWord: @escaping () -> Void,
        onSpeakSentence: @escaping () -> Void,
        onSave: @escaping () -> Void
    ) {
        let content = QuickPopupView(
            entry: entry,
            onSpeakWord: onSpeakWord,
            onSpeakSentence: onSpeakSentence,
            onSave: onSave
        )

        let hostingView = NSHostingView(rootView: content)
        hostingView.frame = NSRect(x: 0, y: 0, width: 320, height: 168)

        if panel == nil {
            let newPanel = NSPanel(
                contentRect: hostingView.frame,
                styleMask: [.nonactivatingPanel, .borderless],
                backing: .buffered,
                defer: false
            )
            newPanel.isFloatingPanel = true
            newPanel.level = .statusBar
            newPanel.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary, .transient]
            newPanel.backgroundColor = .clear
            newPanel.isOpaque = false
            newPanel.hasShadow = true
            newPanel.hidesOnDeactivate = false
            newPanel.ignoresMouseEvents = false
            newPanel.isMovableByWindowBackground = true
            newPanel.isMovable = true
            panel = newPanel
        }

        guard let panel else { return }
        panel.contentView = hostingView
        panel.setContentSize(hostingView.frame.size)
        panel.setFrameOrigin(position(for: panel.frame.size))
        panel.orderFrontRegardless()

        installTrackingMonitor(for: panel)
        scheduleHide(after: 8.0)
    }

    func hide() {
        hideTimer?.invalidate()
        panel?.orderOut(nil)
    }

    private func scheduleHide(after delay: TimeInterval) {
        hideTimer?.invalidate()
        hideTimer = Timer.scheduledTimer(withTimeInterval: delay, repeats: false) { [weak self] _ in
            Task { @MainActor in
                self?.hide()
            }
        }
    }

    private func installTrackingMonitor(for panel: NSPanel) {
        if let trackingMonitor {
            NSEvent.removeMonitor(trackingMonitor)
        }

        trackingMonitor = NSEvent.addGlobalMonitorForEvents(matching: [.mouseMoved, .leftMouseDragged, .leftMouseUp, .rightMouseUp]) { [weak self, weak panel] _ in
            Task { @MainActor in
                guard let self, let panel else { return }
                let mouseLocation = NSEvent.mouseLocation
                if panel.frame.insetBy(dx: -10, dy: -10).contains(mouseLocation) {
                    self.hideTimer?.invalidate()
                } else if panel.isVisible {
                    self.scheduleHide(after: 1.4)
                }
            }
        }
    }

    private func position(for size: CGSize) -> NSPoint {
        let mouse = NSEvent.mouseLocation
        let screen = NSScreen.screens.first { NSMouseInRect(mouse, $0.frame, false) } ?? NSScreen.main
        let visibleFrame = screen?.visibleFrame ?? .zero

        let x = min(max(mouse.x - size.width / 2, visibleFrame.minX + 12), visibleFrame.maxX - size.width - 12)
        let y = min(max(mouse.y - size.height - 18, visibleFrame.minY + 12), visibleFrame.maxY - size.height - 12)

        return NSPoint(x: x, y: y)
    }
}

private struct QuickPopupView: View {
    let entry: WordEntry
    let onSpeakWord: () -> Void
    let onSpeakSentence: () -> Void
    let onSave: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                Text(entry.word)
                    .font(.system(size: 22, weight: .bold))
                Spacer()
                Text("Quick Look")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Text(entry.exampleSentence)
                .font(.system(size: 14, weight: .medium))
                .foregroundStyle(.primary)
                .lineLimit(3)

            HStack(spacing: 8) {
                Button("Speak Word", action: onSpeakWord)
                Button("Speak Example", action: onSpeakSentence)
                Button("Save", action: onSave)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.small)
        }
        .padding(16)
        .frame(width: 320, alignment: .leading)
        .background(Color.black)
        .foregroundStyle(.white)
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(.white.opacity(0.18), lineWidth: 1)
        }
    }
}
