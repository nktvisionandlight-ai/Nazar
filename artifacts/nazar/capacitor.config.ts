import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.nazar.journal",
  appName: "Nazar",
  webDir: "dist/public",
  bundledWebRuntime: false,
  ios: {
    contentInset: "automatic",
  },
};

export default config;
