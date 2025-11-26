import React from 'react';
import logoHorizontal from '@/assets/brand/logo-horizontal.svg';
import logoIcon from '@/assets/brand/logo-icon.svg';
import logoMonochrome from '@/assets/brand/logo-monochrome.svg';
import logoReversed from '@/assets/brand/logo-reversed.svg';

export default function BrandLogo({
    width = 160,
    alt = 'Tapin logo',
    className = 'logo',
    variant = 'horizontal', // 'horizontal' | 'icon' | 'monochrome' | 'reversed'
}) {
    let src = logoHorizontal;
    if (variant === 'icon') src = logoIcon;
    else if (variant === 'monochrome') src = logoMonochrome;
    else if (variant === 'reversed') src = logoReversed;

    return (
        <img
            src={src}
            alt={alt}
            className={className}
            style={{ width, height: 'auto', objectFit: 'contain' }}
        />
    );
}
