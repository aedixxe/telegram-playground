# Demo chats checkpoint (Xcode 27)

This checkpoint contains a local demo account and seeded conversations for iOS Simulator. It includes the small changes needed to build and open the chats with Xcode 27. The attachment button uses Telegram's regular behavior; there is no hold-menu experiment in this checkpoint.

## Generate and run

1. Install Xcode 27 and its iOS Simulator runtime.
2. Copy `demo-chat-configuration.example.json` to `build-input/local-demo-configuration.json`. The demo account uses local data, so the example's zero API ID and hash are sufficient for this simulator build. The copied file is ignored by Git.
3. From the repository root, generate the Xcode project:

   ```sh
   python3 build-system/Make/Make.py \
     --overrideXcodeVersion \
     --cacheDir=build-input/bazel-cache \
     generateProject \
     --configurationPath=build-input/local-demo-configuration.json \
     --disableExtensions \
     --disableProvisioningProfiles \
     --xcodeManagedCodesigning
   ```

4. Open `Telegram/Telegram.xcodeproj`, select the `Telegram` scheme and an iOS 27 simulator, then run. The generated Xcode project is ignored by Git and can be regenerated with the command above.

The demo activates only in a Debug build whose bundle identifier ends in `.TelegramQuickAttach`. No Telegram account or `my.telegram.org` API credentials are needed to browse the seeded chats. Real Telegram login is outside this demo setup.

To restart an experiment from this checkpoint, create a new Git branch from the checkpoint tag before editing the code.
