import { definePreset, palette } from '@primeuix/themes'
import Aura from '@primeuix/themes/aura'

const BRAND_PRIMARY = '#025EA1'

export const MyPreset = definePreset(Aura, {
  semantic: {
    primary: palette(BRAND_PRIMARY),
  },
  components: {
    button: {
      root: {
        paddingX: '12px',
        paddingY: '4px',
      },
    },
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
    colorPicker: {
      panel: {
        borderColor: BRAND_PRIMARY,
      },
      handle: {
        color: BRAND_PRIMARY,
      },
    },
    select: {
      dropdown: {
        color: BRAND_PRIMARY,
      },
      root: {
        borderColor: '{primary.100}',
        hoverBorderColor: '{primary.400}',
        focusBorderColor: '{primary.600}',

        placeholderColor: BRAND_PRIMARY,
        color: BRAND_PRIMARY,
      },
    },
    avatar: {
      root: {
        width: 'auto',
        height: 'auto',
      },
    },
  },
})
