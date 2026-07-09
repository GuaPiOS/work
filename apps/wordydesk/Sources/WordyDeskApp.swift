import SwiftUI

@main
struct WordyDeskApp: App {
    @NSApplicationDelegateAdaptor(WordyDeskAppDelegate.self) private var appDelegate
    @StateObject private var appModel: AppModel

    init() {
        guard AppInstanceManager.prepareForLaunch() else {
            exit(0)
        }

        let model = AppModel()
        _appModel = StateObject(wrappedValue: model)
        appDelegate.configure(with: model)
    }

    var body: some Scene {
        MenuBarExtra("WordyDesk", systemImage: "text.viewfinder") {
            ContentView()
                .environmentObject(appModel)
                .environmentObject(appModel.preferences)
                .frame(width: 410)
        }
        .menuBarExtraStyle(.window)

        Window("WordyDesk", id: "dashboard") {
            ContentView()
                .environmentObject(appModel)
                .environmentObject(appModel.preferences)
                .frame(minWidth: 420, idealWidth: 560, maxWidth: 900, minHeight: 560, idealHeight: 700, maxHeight: 1100)
        }
        .defaultSize(width: 560, height: 700)

        Settings {
            SettingsView()
                .environmentObject(appModel)
                .environmentObject(appModel.preferences)
                .frame(width: 480, height: 360)
        }
    }
}
