// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "WordyDesk",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(
            name: "WordyDesk",
            targets: ["WordyDesk"]
        )
    ],
    targets: [
        .executableTarget(
            name: "WordyDesk",
            path: "Sources"
        )
    ]
)
