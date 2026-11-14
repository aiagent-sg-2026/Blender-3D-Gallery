import * as THREE from 'three';
import { createVisitorCustomization } from '../../models/gjh-visitor-v3/customization.js';
import '../visitor-v2/style.css';

// Gallery controls demonstrate authored clips and cosmetic choices; they do
// not claim to implement the mall's item, cart, seat or elevator state.
export default function createVisitorDemo({model, clips, container, invalidate}) {
  const custom = createVisitorCustomization(model);
  const mixer = new THREE.AnimationMixer(model);
  const available = new Map(clips.map(clip => [clip.name, clip]));
  const toolbar = document.createElement('section');
  toolbar.className = 'visitor-v2-controls';
  toolbar.setAttribute('aria-label', 'Visitor appearance and animation');
  const heading = document.createElement('strong');
  heading.textContent = 'Visitor appearance and animation';
  const note = document.createElement('p');
  note.textContent = 'Animation previews show poses only; mall interactions are handled by the mall.';
  toolbar.append(heading, note);
  const fields = document.createElement('div');
  fields.className = 'visitor-v2-fields';
  toolbar.append(fields);
  const selects = {};
  function select(key, label, options, onChange) {
    const wrapper = document.createElement('label');
    wrapper.textContent = label;
    const input = document.createElement('select');
    input.dataset.visitorControl = key;
    for (const [value, text] of options) {
      const option = document.createElement('option');
      option.value = value; option.textContent = text; input.append(option);
    }
    input.addEventListener('change', () => { onChange(input.value); invalidate(); });
    wrapper.append(input); fields.append(wrapper); selects[key] = input;
  }
  select('hair', 'Hair', [['wavy', 'Wavy'], ['short', 'Short']], value => custom.apply({hair:value}));
  select('hairColor', 'Hair colour', [['black', 'Black'], ['brown', 'Brown']], value => custom.apply({hairColor:value}));
  select('outfit', 'Top', [['hoodie', 'Hoodie'], ['tee', 'T-shirt only']], value => custom.apply({outfit:value}));
  select('skin', 'Skin tone', [['light', 'Light'], ['medium', 'Medium'], ['dark', 'Dark']], value => custom.apply({skin:value}));
  for (const key of ['backpack', 'badge', 'watch'])
    select(key, key[0].toUpperCase() + key.slice(1), [['on', 'On'], ['off', 'Off']], value => custom.apply({[key]:value === 'on'}));
  const names = [['idle','Idle'], ['walk','Walk'], ['run','Run'], ['turn_left','Turn left'], ['turn_right','Turn right'],
    ['sit_down','Sit down'], ['stand_up','Stand up'], ['pick_up','Pick up'], ['carry','Carry'], ['wave','Wave'],
    ['point','Point'], ['push_cart','Push cart']];
  let action = null, playing = false;
  function play(name) {
    const clip = available.get(name);
    if (!clip) throw new Error(`Visitor animation missing: ${name}`);
    mixer.stopAllAction();
    action = mixer.clipAction(clip);
    action.reset();
    const loop = ['idle','walk','run','carry','push_cart'].includes(name);
    action.setLoop(loop ? THREE.LoopRepeat : THREE.LoopOnce, loop ? Infinity : 1);
    action.clampWhenFinished = !loop;
    action.play();
    playing = !matchMedia('(prefers-reduced-motion: reduce)').matches;
    mixer.update(0);
  }
  select('animation', 'Animation', names, play);
  container.insertAdjacentElement('afterend', toolbar);
  function reset() {
    custom.apply({hair:'wavy',hairColor:'black',outfit:'hoodie',skin:'light',backpack:true,badge:true,watch:true});
    for (const [key, value] of Object.entries({hair:'wavy',hairColor:'black',outfit:'hoodie',skin:'light',backpack:'on',badge:'on',watch:'on',animation:'idle'}))
      selects[key].value = value;
    play('idle');
  }
  reset();
  return {
    reset,
    update(dt) {
      if (!playing || !action) return false;
      mixer.update(Math.min(Math.max(dt, 0), .05));
      if (action.paused) playing = false;
      return playing;
    },
    dispose() { playing = false; mixer.stopAllAction(); mixer.uncacheRoot(model); custom.dispose(); toolbar.remove(); },
  };
}
