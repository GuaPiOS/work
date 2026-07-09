import Foundation

enum WordyDeskPaths {
    static var applicationSupportDirectory: URL {
        let baseURL = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        return baseURL.appendingPathComponent("WordyDesk", isDirectory: true)
    }

    static var legacyDocumentsDirectory: URL {
        let baseURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
        return baseURL.appendingPathComponent("WordyDesk", isDirectory: true)
    }

    static var favoritesFileURL: URL {
        applicationSupportDirectory.appendingPathComponent("collected-words.md")
    }

    static var studyProgressFileURL: URL {
        applicationSupportDirectory.appendingPathComponent("study-progress.json")
    }

    static func migrateLegacyFilesIfNeeded() throws {
        let fileManager = FileManager.default
        let targetDirectory = applicationSupportDirectory
        try fileManager.createDirectory(at: targetDirectory, withIntermediateDirectories: true)

        let migrations: [(from: URL, to: URL)] = [
            (legacyDocumentsDirectory.appendingPathComponent("collected-words.md"), favoritesFileURL),
            (legacyDocumentsDirectory.appendingPathComponent("study-progress.json"), studyProgressFileURL)
        ]

        for migration in migrations {
            guard fileManager.fileExists(atPath: migration.from.path) else { continue }
            guard !fileManager.fileExists(atPath: migration.to.path) else { continue }
            try fileManager.copyItem(at: migration.from, to: migration.to)
        }
    }
}
