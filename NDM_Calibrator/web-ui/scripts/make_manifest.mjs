/**
 * Generate MANIFEST.json and SHA256SUMS.txt for the deliverable.
 * Excludes node_modules, .git, dist cache, and old zips.
 */
import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { dirname } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");

const EXCLUDE_DIRS = new Set([
  "node_modules", ".git", "dist", ".vscode", ".idea",
  "screenshots", "deliverable", "logs",
]);
const EXCLUDE_FILES = new Set([
  "MANIFEST.json", "SHA256SUMS.txt",
]);

function walk(dir, out = []) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith(".") && entry.name !== ".gitignore") continue;
    if (EXCLUDE_DIRS.has(entry.name)) continue;
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full, out);
    } else if (entry.isFile() && !EXCLUDE_FILES.has(entry.name)) {
      out.push(full);
    }
  }
  return out;
}

const files = walk(ROOT).sort();
const manifest = [];
const sums = [];

for (const f of files) {
  const rel = relative(ROOT, f).replace(/\\/g, "/");
  const data = readFileSync(f);
  const hash = createHash("sha256").update(data).digest("hex");
  const size = statSync(f).size;
  manifest.push({ path: rel, size, sha256: hash });
  sums.push(`${hash}  ${rel}`);
}

writeFileSync(join(ROOT, "MANIFEST.json"), JSON.stringify(manifest, null, 2));
writeFileSync(join(ROOT, "SHA256SUMS.txt"), sums.join("\n") + "\n");
console.log(`MANIFEST: ${manifest.length} files`);
