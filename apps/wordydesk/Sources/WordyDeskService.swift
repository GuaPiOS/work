import AppKit
import Foundation

final class WordyDeskServiceProvider: NSObject {
    weak var appModel: AppModel?

    @objc(lookupSelectedText:userData:error:)
    @MainActor
    func lookupSelectedText(
        _ pasteboard: NSPasteboard,
        userData: String?,
        error: AutoreleasingUnsafeMutablePointer<NSString?>
    ) {
        guard let text = pasteboard.string(forType: .string), !text.isEmpty else {
            error.pointee = "WordyDesk could not read the selected text." as NSString
            return
        }

        let appModel = appModel
        Task { @MainActor in
            await appModel?.handleIncomingText(text, trigger: .service)
        }
    }
}

@MainActor
final class WordyDeskAppDelegate: NSObject, NSApplicationDelegate {
    private let serviceProvider = WordyDeskServiceProvider()
    private weak var appModel: AppModel?

    @MainActor
    func configure(with appModel: AppModel) {
        self.appModel = appModel
        serviceProvider.appModel = appModel
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        serviceProvider.appModel = appModel
        NSApp.servicesProvider = serviceProvider
        NSUpdateDynamicServices()
    }
}
