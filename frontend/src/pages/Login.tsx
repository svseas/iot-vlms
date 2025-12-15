import React from 'react';
import { Form, Input, Button, Card, message, Typography } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../stores/authStore';
import type { LoginRequest } from '../types';

const { Title, Text } = Typography;

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { login, isLoading, error, clearError } = useAuthStore();
  const [form] = Form.useForm();

  const handleSubmit = async (values: LoginRequest) => {
    try {
      await login(values);
      message.success(t('auth.loginSuccess'));
      navigate('/');
    } catch {
      message.error(error || t('auth.loginFailed'));
    }
  };

  React.useEffect(() => {
    if (error) {
      message.error(error);
      clearError();
    }
  }, [error, clearError]);

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)',
      }}
    >
      <Card
        style={{
          width: 400,
          boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title level={2} style={{ marginBottom: 8 }}>
            VLMS
          </Title>
          <Text type="secondary">{t('auth.systemName')}</Text>
        </div>

        <Form form={form} onFinish={handleSubmit} layout="vertical" size="large">
          <Form.Item
            name="email"
            rules={[
              { required: true, message: t('auth.emailRequired') },
              { type: 'email', message: t('auth.emailInvalid') },
            ]}
          >
            <Input prefix={<UserOutlined />} placeholder={t('auth.email')} />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: t('auth.passwordRequired') }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder={t('auth.password')} />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={isLoading}>
              {t('auth.login')}
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Login;
