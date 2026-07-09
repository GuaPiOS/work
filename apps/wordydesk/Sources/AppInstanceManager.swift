import AppKit
import Darwin
import Foundation

@MainActor
enum AppInstanceManager {
    private static var lockFileDescriptor: CInt = -1

    static func prepareForLaunch() -> Bool {
        guard acquireSingleInstanceLock() else {
            return false
        }

        terminateOtherInstances()
        return true
    }

    static func terminateOtherInstances() {
        guard let bundleIdentifier = Bundle.main.bundleIdentifier else { return }
        let currentProcessIdentifier = ProcessInfo.processInfo.processIdentifier

        let others = NSRunningApplication.runningApplications(withBundleIdentifier: bundleIdentifier)
            .filter { $0.processIdentifier != currentProcessIdentifier }

        for app in others {
            app.terminate()
        }
    }

    static func restartCurrentApp() {
        relaunchAfterDelay()
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
            NSApp.terminate(nil)
        }
    }

    static func terminateAllInstancesAndCurrent() {
        terminateOtherInstances()
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            NSApp.terminate(nil)
        }
    }

    private static func acquireSingleInstanceLock() -> Bool {
        if lockFileDescriptor != -1 {
            return true
        }

        let directoryURL = FileManager.default.temporaryDirectory.appendingPathComponent("WordyDesk", isDirectory: true)
        try? FileManager.default.createDirectory(at: directoryURL, withIntermediateDirectories: true)

        let lockFilePath = directoryURL.appendingPathComponent("singleton.lock").path
        let descriptor = open(lockFilePath, O_CREAT | O_RDWR, S_IRUSR | S_IWUSR)
        guard descriptor != -1 else {
            return false
        }

        if flock(descriptor, LOCK_EX | LOCK_NB) != 0 {
            close(descriptor)
            return false
        }

        lockFileDescriptor = descriptor
        return true
    }

    private static func relaunchAfterDelay() {
        let bundlePath = Bundle.main.bundleURL.path
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/bin/sh")
        process.arguments = ["-c", "sleep 0.4; open '\(bundlePath)'"]
        try? process.run()
    }
}
