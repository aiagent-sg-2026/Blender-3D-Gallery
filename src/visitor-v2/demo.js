import * as THREE from 'three';
import { createVisitorCustomization } from '../../models/gjh-mall-visitor-v2/customization.js';
import './style.css';

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
  select('hair', 'Hair', [['swept', 'Swept'], ['short', 'Short']], value => custom.apply({hair:value}));
  select('hairColor', 'Hair colour', [['brown', 'Brown'], ['black', 'Black']], value => custom.apply({hairColor:value}));
  select('outfit', 'Top', [['polo', 'Polo'], ['hoodie', 'Hoodie']], value => custom.apply({outfit:value}));
  select('skin', 'Skin tone', [['light', 'Light'], ['medium', 'Medium'], ['dark', 'Dark']], value => custom.apply({skin:value}));
  for (const key of ['glasses', 'backpack', 'watch'])
    select(key, key[0].toUpperCase() + key.slice(1), [['on', 'On'], ['off', 'Off']], value => custom.apply({[key]:value === 'on'}));
  const names = [['idle','Idle'], ['walk','Walk'], ['sprint','Run'], ['sit','Sit'], ['stand','Stand'],
    ['pickup','Pick up'], ['place','Put down'], ['push','Push'], ['elevator','Reach']];
  let action = null, playing = false;
  function play(name) {
    const clip = available.get(name);
    if (!clip) throw new Error(`Visitor animation missing: ${name}`);
    mixer.stopAllAction();
    action = mixer.clipAction(clip);
    action.reset();
    const loop = ['idle','walk','sprint','push'].includes(name);
    action.setLoop(loop ? THREE.LoopRepeat : THREE.LoopOnce, loop ? Infinity : 1);
    action.clampWhenFinished = !loop;
    action.play();
    playing = !matchMedia('(prefers-reduced-motion: reduce)').matches;
    mixer.update(0);
  }
  select('animation', 'Animation', names, play);
  container.insertAdjacentElement('afterend', toolbar);
  function reset() {
    custom.apply({hair:'swept',hairColor:'brown',outfit:'polo',skin:'light',glasses:true,backpack:true,watch:true});
    for (const [key, value] of Object.entries({hair:'swept',hairColor:'brown',outfit:'polo',skin:'light',glasses:'on',backpack:'on',watch:'on',animation:'idle'}))
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
