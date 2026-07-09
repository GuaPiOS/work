import SwiftUI

struct OnboardingView: View {
    let onDismiss: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("WordyDesk")
                .font(.system(size: 28, weight: .semibold))

            Text("Select a word. Save what matters. Review when it is due.")
                .font(.title3)
                .foregroundStyle(.secondary)

            VStack(alignment: .leading, spacing: 10) {
                Text("1. Select a word in any app.")
                Text("2. Let the floating card read it, or press play yourself.")
                Text("3. Save it and review it later with spaced repetition.")
            }
            .font(.body)

            Button("Start") {
                onDismiss()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding(28)
        .frame(width: 420)
    }
}
