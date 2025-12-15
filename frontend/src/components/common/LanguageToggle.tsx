import React from 'react';
import { Dropdown, Button } from 'antd';
import { GlobalOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import type { MenuProps } from 'antd';

const languages = [
  { key: 'vi', label: '🇻🇳 Tiếng Việt', flag: '🇻🇳' },
  { key: 'en', label: '🇬🇧 English', flag: '🇬🇧' },
];

const LanguageToggle: React.FC = () => {
  const { i18n } = useTranslation();

  const handleLanguageChange: MenuProps['onClick'] = ({ key }) => {
    i18n.changeLanguage(key);
    localStorage.setItem('language', key);
  };

  const currentLanguage = languages.find((l) => l.key === i18n.language) || languages[0];

  const items: MenuProps['items'] = languages.map((lang) => ({
    key: lang.key,
    label: (
      <span style={{ fontWeight: lang.key === i18n.language ? 'bold' : 'normal' }}>
        {lang.label}
      </span>
    ),
  }));

  return (
    <Dropdown
      menu={{ items, onClick: handleLanguageChange }}
      placement="bottomRight"
      trigger={['click']}
    >
      <Button type="text" icon={<GlobalOutlined />}>
        {currentLanguage.flag} {currentLanguage.key.toUpperCase()}
      </Button>
    </Dropdown>
  );
};

export default LanguageToggle;
