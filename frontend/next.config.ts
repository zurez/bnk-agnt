import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Empty turbopack config to allow dev mode with webpack config
  turbopack: {},
  
  // Enable standalone output for Docker optimization
  output: "standalone",
  
  // Externalize packages that have issues with bundling (e.g., test files)
  serverExternalPackages: ['pino', 'thread-stream', 'pino-pretty'],
  
  webpack: (config) => {
    // Ignore test files from node_modules to prevent bundling dev dependencies
    config.plugins.push(
      new (require('webpack').IgnorePlugin)({
        resourceRegExp: /\/(test|tests|__tests__)\//,
        contextRegExp: /node_modules/,
      }),
      new (require('webpack').IgnorePlugin)({
        resourceRegExp: /thread-stream\/test/,
      })
    );
    
    return config;
  },
};

export default nextConfig;
