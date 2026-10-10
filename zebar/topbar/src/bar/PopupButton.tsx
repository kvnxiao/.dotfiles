import { onMount, type ParentComponent } from 'solid-js';

import { createPopup } from '../lib/popup';

export interface PopupButtonProps {
  popup: string;
  width: number;
  height: number;
  label: string;
  id?: string;
}

export const PopupButton: ParentComponent<PopupButtonProps> = props => {
  let button!: HTMLButtonElement;
  let popup: ReturnType<typeof createPopup> | undefined;
  onMount(() => {
    popup = createPopup(props.popup, button, props.width, props.height);
  });
  return (
    <button
      ref={button}
      id={props.id}
      aria-label={props.label}
      onPointerDown={() => popup?.press()}
      onClick={() => void popup?.toggle()}
    >
      {props.children}
    </button>
  );
};
