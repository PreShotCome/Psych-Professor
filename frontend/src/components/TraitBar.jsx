const TRAIT_POLES = {
  moral:        ['good',       'evil'],
  law:          ['lawful',     'chaotic'],
  aggression:   ['passive',    'aggressive'],
  deception:    ['honest',     'deceptive'],
  empathy:      ['cold',       'empathetic'],
  dominance:    ['submissive', 'dominant'],
  impulsivity:  ['measured',   'impulsive'],
  curiosity:    ['incurious',  'curious'],
  paranoia:     ['trusting',   'paranoid'],
  manipulation: ['direct',     'manipulative'],
}

function traitColor(trait, value) {
  if (Math.abs(value) < 0.05) return 'var(--text-dim)'
  const isPos = value > 0
  switch (trait) {
    case 'moral':        return isPos ? 'var(--evil)' : 'var(--good)'
    case 'law':          return isPos ? 'var(--warn)' : '#3b82f6'
    case 'aggression':   return isPos ? 'var(--evil)' : 'var(--text-muted)'
    case 'deception':    return isPos ? 'var(--purple)' : 'var(--text-muted)'
    case 'empathy':      return isPos ? 'var(--cyan)' : 'var(--text-muted)'
    case 'dominance':    return isPos ? 'var(--warn)' : 'var(--text-muted)'
    case 'impulsivity':  return isPos ? 'var(--orange)' : 'var(--text-muted)'
    case 'curiosity':    return isPos ? 'var(--good)' : 'var(--text-muted)'
    case 'paranoia':     return isPos ? 'var(--evil)' : 'var(--text-muted)'
    case 'manipulation': return isPos ? 'var(--purple)' : 'var(--text-muted)'
    default:             return 'var(--accent)'
  }
}

export function traitChipColor(trait, value) {
  return traitColor(trait, value)
}

export default function TraitBar({ trait, value }) {
  const clamped = Math.max(-1, Math.min(1, value))
  const isPos = clamped >= 0
  const absVal = Math.abs(clamped)
  const color = traitColor(trait, clamped)
  const poles = TRAIT_POLES[trait] || ['low', 'high']

  const fillStyle = {
    backgroundColor: color,
    width: `${absVal * 50}%`,
    left: isPos ? '50%' : `${(0.5 + clamped / 2) * 100}%`,
  }

  const poleLabel = Math.abs(clamped) >= 0.1
    ? (isPos ? poles[1] : poles[0])
    : '—'

  return (
    <div className="trait-row" title={`${trait}: ${clamped >= 0 ? '+' : ''}${clamped.toFixed(2)} (${poleLabel})`}>
      <span className="trait-label">{trait}</span>
      <div className="trait-track">
        <div className="trait-center-tick" />
        <div className="trait-fill" style={fillStyle} />
      </div>
      <span className="trait-num" style={{ color }}>
        {clamped >= 0 ? '+' : ''}{clamped.toFixed(2)}
      </span>
    </div>
  )
}
