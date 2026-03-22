#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const REGISTRY_PATH = path.resolve(__dirname, '..', 'fragments_users.json');

function parseArgs(argv) {
  const out = {};

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith('--')) continue;
    const key = token.slice(2);
    const next = argv[index + 1];

    if (!next || next.startsWith('--')) {
      out[key] = 'true';
      continue;
    }

    out[key] = next;
    index += 1;
  }

  return out;
}

function slugify(value) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
}

function normalizeHandle(value, fallbackName) {
  const trimmed = String(value || '').trim();
  if (!trimmed) {
    return `@${slugify(fallbackName || 'family') || 'family'}`;
  }
  return trimmed.startsWith('@') ? trimmed : `@${trimmed}`;
}

function toSecretName(explicitValue, id) {
  if (explicitValue) {
    return String(explicitValue).trim().toUpperCase();
  }
  return `FRAGMENTS_KEY_${String(id || '').trim().replace(/[^a-z0-9]+/gi, '_').toUpperCase()}`;
}

function readRegistry() {
  return JSON.parse(fs.readFileSync(REGISTRY_PATH, 'utf8'));
}

function usage() {
  console.log('Usage: node tools/provision_fragments_user.js --name "Daughter Name" --avatar "Images/family/daughter.jpg" [--id daughter_name] [--handle @daughter_name] [--secret FRAGMENTS_KEY_DAUGHTER_NAME] [--verified false]');
}

function main() {
  const args = parseArgs(process.argv.slice(2));

  if (!args.name || !args.avatar) {
    usage();
    process.exitCode = 1;
    return;
  }

  const registry = readRegistry();
  const id = args.id ? slugify(args.id) : slugify(args.name);
  const name = String(args.name).trim();
  const handle = normalizeHandle(args.handle, name);
  const avatar = String(args.avatar).trim();
  const publishKeySecretName = toSecretName(args.secret, id);
  const verified = String(args.verified || 'false').trim().toLowerCase() === 'true';

  const duplicateId = registry.find((entry) => entry.id === id);
  const duplicateHandle = registry.find((entry) => String(entry.handle || '').toLowerCase() === handle.toLowerCase());
  const duplicateSecret = registry.find((entry) => String(entry.publishKeySecretName || '').toUpperCase() === publishKeySecretName);

  if (duplicateId || duplicateHandle || duplicateSecret) {
    console.error('Registry conflict detected.');
    if (duplicateId) console.error(`- id already exists: ${id}`);
    if (duplicateHandle) console.error(`- handle already exists: ${handle}`);
    if (duplicateSecret) console.error(`- secret name already exists: ${publishKeySecretName}`);
    process.exitCode = 1;
    return;
  }

  const avatarExists = fs.existsSync(path.resolve(__dirname, '..', avatar));
  const suggestedEntry = {
    id,
    name,
    handle,
    avatar,
    publishKeySecretName,
    verified
  };

  console.log('Suggested registry entry:\n');
  console.log(JSON.stringify(suggestedEntry, null, 2));
  console.log('\nProvisioning checklist:\n');
  console.log(`1. Add this entry to fragments_users.json.`);
  console.log(`2. ${avatarExists ? 'Avatar file confirmed.' : 'Add the avatar file first.'} (${avatar})`);
  console.log(`3. Create the Cloudflare Worker secret:`);
  console.log(`   cd cloudflare/otw-fragments-publish && wrangler secret put ${publishKeySecretName}`);
  console.log(`4. Hand the user the frgm<nts app URL and only their publish key.`);
  console.log(`5. On their device, open frgmnts_publisher.html, paste the key, and confirm the registered identity card matches ${name} (${handle}).`);
}

main();
