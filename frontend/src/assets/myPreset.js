import { definePreset, palette } from '@primeuix/themes'
import Aura from '@primeuix/themes/aura'

export const MyPreset = definePreset(Aura, {
  semantic: {
    primary: palette('#025EA1'),
  },
  components: {
    card: {
      border: {
        radius: '4px',
      },
      body: {
        padding: '10px',
      },
      title: {
        font: {
          size: '1.25rem',
          weight: 'bold',
          color: '{primary}',
        },
      },
    },
    select: {
      dropdown: {
        color: '#025EA1',
      },
      root: {
        borderColor: '{primary.100}',
        hoverBorderColor: '{primary.400}',
        focusBorderColor: '{primary.600}',

        placeholderColor: '#025EA1',
        color: '#025EA1',
      },
    },
  },
})
