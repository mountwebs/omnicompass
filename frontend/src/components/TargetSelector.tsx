import React from 'react';

interface TargetSelectorProps {
    currentTarget: string;
    onSelectTarget: (target: string) => void;
}

export const TargetSelector: React.FC<TargetSelectorProps> = ({ currentTarget, onSelectTarget }) => {
    return (
        <div style={{ position: 'absolute', top: 10, right: 10, background: 'rgba(0,0,0,0.5)', padding: 10 }}>
            <select 
                value={currentTarget} 
                onChange={(e) => onSelectTarget(e.target.value)}
                style={{ fontSize: '16px', padding: '5px' }}
            >
                <option value="SUN">Sun</option>
                <option value="MARS">Mars</option>
                <option value="VENUS">Venus</option>
                <option value="SATURN">Saturn</option>
                <option value="JUPITER">Jupiter</option>
            </select>
        </div>
    );
};
