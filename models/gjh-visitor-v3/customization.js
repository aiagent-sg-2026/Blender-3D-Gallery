/** Apply per-instance v3 visitor choices without changing shared source materials. */
export function createVisitorCustomization(root) {
  const parts = [];
  root.traverse(node => {
    if (node.isMesh && node.name.startsWith('V3_')) parts.push(node);
  });
  const find = prefix => parts.filter(part => part.name.startsWith(prefix));
  const groups = {
    hair: find('V3_hair_'),
    alternateHair: find('V3_hair_alt_'),
    jacket: find('V3_jacket_'),
    skin: find('V3_body_Warm_peach_skin'),
    brows: find('V3_body_Brow'),
    backpack: find('V3_backpack_'),
    badge: find('V3_badge_'),
    watch: find('V3_watch_'),
  };
  groups.hair = groups.hair.filter(part => !groups.alternateHair.includes(part));
  if (Object.values(groups).some(group => group.length === 0))
    throw new Error('Visitor customization components are missing');
  const originals = new Map();
  for (const part of [...groups.hair, ...groups.alternateHair, ...groups.brows, ...groups.skin]) {
    originals.set(part, part.material);
    part.material = part.material.clone();
  }
  const skinColors = {light: 0xe2ac82, medium: 0xb7774d, dark: 0x75472f};
  const hairColors = {black: 0x1e1b1e, brown: 0x412b1c};
  let state = {hair: 'wavy', hairColor: 'black', outfit: 'hoodie', skin: 'light', backpack: true, badge: true, watch: true};
  const visible = (group, value) => { for (const part of group) part.visible = value; };
  function apply(changes = {}) {
    const next = {...state, ...changes};
    if (!['wavy', 'short'].includes(next.hair) || !(next.hairColor in hairColors) ||
        !['hoodie', 'tee'].includes(next.outfit) || !(next.skin in skinColors) ||
        !['backpack', 'badge', 'watch'].every(key => typeof next[key] === 'boolean'))
      throw new TypeError('Invalid visitor customization');
    visible(groups.hair, next.hair === 'wavy');
    visible(groups.alternateHair, next.hair === 'short');
    visible(groups.jacket, next.outfit === 'hoodie');
    for (const part of [...groups.hair, ...groups.alternateHair, ...groups.brows]) part.material.color.setHex(hairColors[next.hairColor]);
    for (const part of groups.skin) part.material.color.setHex(skinColors[next.skin]);
    for (const key of ['backpack', 'badge', 'watch']) visible(groups[key], next[key]);
    state = next;
    return {...state};
  }
  apply();
  return {
    apply,
    get state() { return {...state}; },
    dispose() {
      for (const [part, original] of originals) {
        part.material.dispose();
        part.material = original;
      }
      originals.clear();
    },
  };
}
