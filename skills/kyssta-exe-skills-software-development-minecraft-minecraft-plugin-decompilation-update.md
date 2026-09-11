---
name: minecraft-plugin-decompilation-update
description: Process for decompiling existing Minecraft plugins (without source) and updating them to work with newer Paper/Spigot versions
tags: [minecraft, plugin, decompilation, update, paper, spigot, java, gradle]
---

# Minecraft Plugin Decompilation and Update

This skill covers the process of taking existing Minecraft plugin JAR files (without source code), decompiling them, analyzing the code, and updating them to work with newer versions of Paper/Spigot.

## When to Use This Skill

- User provides plugin JAR files without source code
- Need to update plugins for newer Minecraft/Paper versions
- Plugins fail to load on newer server versions due to API changes
- Want to modify or extend existing plugin functionality
- Need to understand how a plugin works by examining its code
- User requests removal of unnecessary plugins (e.g., knockbacksync, goosesync, TagPlugin, ShieldBreakSound)

## Workflow Overview

1. **Locate and Prepare Plugin JARs**
2. **Decompile JAR Files**
3. **Analyze Code Structure and Dependencies**
4. **Create Build Project**
5. **Adapt Code for Target Version**
6. **Build and Test Updated Plugin**
7. **Deploy to Server**

## Detailed Steps

### 1. Locate and Prepare Plugin JARs

```bash
# Create working directory
mkdir -p /tmp/mc-plugins/{decompile,decompiled,build}

# Copy plugin JARs from server (adjust path as needed)
cp /path/to/server/plugins/*.jar /tmp/mc-plugins/decompile/

# For Paper-patched plugins, also check .paper-remapped/ directory
cp /path/to/server/plugins/.paper-remapped/*.jar /tmp/mc-plugins/decompile/ 2>/dev/null || true
```

### 2. Decompile JAR Files

```bash
# Install Java JDK if needed (Java 21+ recommended for most modern plugins)
# apt-get install -y openjdk-21-jdk

# Download CFR decompiler (recommended for modern Java bytecode)
curl -sL -o /tmp/cfr.jar "https://github.com/leibnitz27/cfr/releases/download/0.152/cfr-0.152.jar"

# Decompile each plugin
for jar in /tmp/mc-plugins/decompile/*.jar; do
    plugin_name=$(basename "$jar" .jar)
    mkdir -p "/tmp/mc-plugins/decompiled/$plugin_name"
    java -jar /tmp/cfr.jar "$jar" --outputdir "/tmp/mc-plugins/decompiled/$plugin_name/"
done
```

### 3. Analyze Code Structure

After decompilation, examine:
- Main plugin class (extends JavaPlugin or custom PluginWrapper)
- Dependencies (import statements reveal required libraries)
- Configuration files (plugin.yml, config.yml, etc.)
- Command and listener structure
- Use of external APIs (PlaceholderAPI, WorldGuard, Adventure, etc.)
- Any version-specific code that may need updating

Key files to examine:
- `plugin.yml` - contains API version, main class, commands, permissions
- Main plugin class - entry point and initialization
- Manager classes - core logic
- Listener classes - event handling
- Utility classes - helper functions

### 4. Create Build Project

For each plugin, create a Gradle or Maven project:

**Gradle build.gradle example:**
```gradle
plugins {
    id 'java'
}

group = 'original.group.id'  // Preserve original group if possible
version = 'original-version' // Keep original version or increment

java {
    // Set based on target Paper version:
    // Paper 1.20.x: Java 17
    // Paper 1.21.x: Java 21
    // Paper 26.x: Java 25
    sourceCompatibility = JavaVersion.VERSION_21
    targetCompatibility = JavaVersion.VERSION_21
}

repositories {
    mavenCentral()
    maven { url = 'https://repo.papermc.io/repository/maven-public/' }
}

dependencies {
    // Use appropriate Paper API version for compilation
    // NOTE: Paper 26.x API not published - use 1.21.4-R0.1-SNAPSHOT for 26.1.2
    compileOnly 'io.papermc.paper:paper-api:1.21.4-R0.1-SNAPSHOT'
    
    // Add other dependencies as needed:
    // compileOnly 'net.kyori:adventure-api:4.12.0'
    // compileOnly 'net.kyori:adventure-platform-bukkit:4.12.0'
    // compileOnly 'me.clip:placeholderapi:2.12.2'
}

tasks.withType(JavaCompile) {
    options.encoding = 'UTF-8'
}

jar {
    // Preserve original JAR name if desired
    archiveFileName = 'original-plugin-name.jar'
    // Or create new versioned name
    // archiveFileName = 'updated-plugin-name-${version}.jar'
}

// Copy resources (plugin.yml, config files, etc.)
processResources {
    from(sourceSets.main.resources) {
        include 'plugin.yml'
        include '*.yml'
        include '*.yaml'
        include 'messages/**'
        include 'menus/**'
    }
}
```

### 5. Adapt Code for Target Version

Common issues when updating to newer Paper versions:

#### ChatColor Replacement
Replace `net.md_5.bungee.api.ChatColor` with Adventure API:
```java
// OLD (BungeeChatColor)
import net.md_5.bungee.api.ChatColor;
String message = ChatColor.GREEN + "Hello " + ChatColor.AQUA + "World!";

// NEW (Adventure API)
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import net.kyori.adventure.text.serializer.legacy.LegacyComponentSerializer;

Component message = Component.text()
    .append(Component.text("Hello ").color(NamedTextColor.GREEN))
    .append(Component.text("World").color(NamedTextColor.AQUA));
// Or using LegacyComponentSerializer for & codes:
Component message = LegacyComponentSerializer.legacySection().deserialize("&aHello &bWorld!");

// Send to player:
player.sendMessage(message);
```

#### PersistentDataContainer Changes
Check for changes in NamespacedKey usage and PersistentDataType.

#### Command Registration
If targeting Paper 26.x as a true Paper plugin (not legacy), use `registerCommand()` instead of `getCommand().setExecutor()`:
```java
// OLD (may fail on Paper 26.x with paper-plugin.yml)
getCommand("mycommand").setExecutor(new MyCommandExecutor());

// NEW (Paper plugin way)
this.registerCommand("mycommand", new MyCommandExecutor());
```
#### Dependency Updates

Check versions of soft dependencies:
- PlaceholderAPI
- WorldGuard
- Vault
- ProtocolLib
- etc.

#### Handling Bundled Utility Libraries

Decompiled plugins (especially from the Xyris/Darkxx ecosystem) often bundle a shared `dev.darkxx.utils` library. Replace these with local reimplementations targeting Paper API directly:

- `PluginWrapper` → `JavaPlugin` directly (remove `start()`/`stop()` callbacks)
- `XyrisCommand` → reimplement locally (⚠️ **duplicate `getPlugin()` pitfall**: both `Command` and `PluginIdentifiableCommand` define this method — keep only the `@Override` version)
- `MiniMessages` → `MiniMessage.miniMessage().deserialize(str)` (Paper bundles Adventure)
- `GuiBuilder/GuiManager/ItemBuilderGUI` → reimplement locally (~170/90/160 lines each)
- `WorldGuardUtil` → reflection-based check (see full Java pattern in `minecraft-plugins` skill → `references/rebranding-darkxx-plugins.md`)
- `Utils.init/uninit` → remove entirely (LicenseManager was its only purpose)
- `Commodore/Brigadier` → do not bundle. Paper provides built-in Brigadier
- **Skript** → remove from compile dependencies entirely. Skript has NO Maven artifact (none of the known coordinates resolve). Use runtime Bukkit API detection: `Bukkit.getPluginManager().getPlugin("Skript") != null`

For a complete class-by-class mapping table including dependency Maven coordinates (PlaceholderAPI 2.11.6, Skript avoidance pattern), see `minecraft-plugins` skill → `references/rebranding-darkxx-plugins.md`.

### 6. Build and Test

```bash
# For Java 21 projects (most common)
./gradlew clean build

# For Java 25 projects (Paper 26.x)
# Ensure JAVA_HOME points to JDK 25
export JAVA_HOME=/path/to/jdk-25
./gradlew clean build

# Locate built JAR
ls build/libs/
```

### 7. Deploy and Test

```bash
# Copy to server plugins directory
cp build/libs/your-plugin.jar /path/to/server/plugins/

# Restart server or use plugin manager to reload
# Check logs for errors
# Test functionality in-game
```

## Version-Specific Considerations

### Paper 1.20.x (MC 1.20.1-1.20.4)
- Requires Java 17
- Uses Adventure API 4.x
- Standard Bukkit API mostly stable

### Paper 1.21.x (MC 1.21.1-1.21.4)
- Requires Java 21
- Adventure API 4.x+
- Some API deprecations (check migration guides)

### Paper 26.x (MC 26.x — Minecraft dropped the "1." prefix in 2025)
- Requires Java 25 for runtime
- Paper API IS published to Maven (`io.papermc.paper:paper-api:26.1.2.build.72-stable`) but it requires Java 25 for dependency resolution — and Gradle 8.x (8.12/8.13/8.15) crashes on JDK 25.0.3 with `> 25.0.3`
- **Workaround**: Compile against `1.21.4-R0.1-SNAPSHOT` with Java 21, run on Paper 26.1.2 with Java 25. The API surface is backward compatible.
- May require `paper-plugin.yml` vs `plugin.yml` considerations (delete paper-plugin.yml to avoid `UnsupportedOperationException` on `getCommand()`)
- Some internal API changes but Bukkit/Spigot API remains compatible

## Troubleshooting

### Compilation Errors
- **Unsupported class version**: JDK version mismatch
- **Cannot find symbol**: Missing dependencies or API changes
- **Package does not exist**: Check repository URLs and dependency versions

### Runtime Errors
- **NoSuchMethodError**: API method changed/removed
- **IllegalAccessError**: Access to internal APIs
- **VerificationError**: Bytecode incompatibility (often JDK version)
- **Plugin fails to load**: Check plugin.yml syntax and main class

### Common Fixes
1. Update dependency versions in build.gradle
2. Replace deprecated API calls with modern equivalents
3. Adjust Java source/target compatibility
4. Check for and remove conflicting files (like paper-plugin.yml when not needed)
5. Use shadows/plugin shading for bundled dependencies if needed

## Best Practices

1. **Preserve original functionality** - don't change behavior unless fixing compatibility
2. **Keep original package structure** when possible for compatibility with existing configs/data
3. **Document changes made** - create a CHANGELOG.md
4. **Test thoroughly** - verify all commands, permissions, and features work
5. **Consider legal implications** - only modify plugins you have rights to modify
6. **Maintain attribution** - keep original authors' credits in plugin.yml and code
7. **Use dependency management** - don't just copy JARs into your project; use proper dependencies
8. **Remove unnecessary plugins** - as per user preference, plugins like knockbacksync, goosesync, TagPlugin, and ShieldBreakSound may be removed if not needed.\n9. **Verify JAR downloads** - always check that downloaded files are actual JARs (use `file <jar>`) and not HTML error pages from retired APIs\n10. **Consider Java version nuances** - For Paper 26.x, the server requires Java 25 to run, but you can often compile against older but compatible API versions (like 1.21.4-R0.1-SNAPSHOT) using Java 21, then run on the actual Paper 26.x server with Java 25\n\n## Support Files\n\n- `references/litebans-decompilation-analysis.md` — Full decompilation analysis of LiteBans v2.12.0 (734 classes, obfuscation analysis, all features, API surface, database architecture, 10-way competitor comparison matrix). Use as reference when building or comparing punishment plugins.
- `references/reflection-based-hooks.md` — Replace compile-time dependencies for optional plugins (WorldGuard, Skript, PlaceholderAPI) with reflection.
- Paper API documentation: https://papermc.io/javadocs/paper/\n\n- Paper API documentation: https://papermc.io/javadocs/paper/\n- Adventure API guide: https://docs.adyrianda.co/\n- SpigotMC API: https://hub.spigotmc.org/javadocs/spigot/\n- CFR Decompiler: https://github.com/leibnitz27/cfr\n- Java Version Requirements: Check Paper version metadata