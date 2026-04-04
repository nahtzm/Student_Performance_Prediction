import React, { useState } from 'react';
import { Layout, Card, Button, Typography, Space, message } from 'antd';
import axios from 'axios';

const { Header, Content, Footer } = Layout;
const { Title, Text } = Typography;

function App() {
  const [loading, setLoading] = useState(false);

  const testBackend = async () => {
    setLoading(true);
    try {
      // Gọi thử đến Backend Python đang chạy ở Port 8000
      const response = await axios.get('http://127.0.0.1:8000/health');
      message.success('Kết nối Backend thành công: ' + response.data.message);
    } catch (error) {
      message.error('Chưa kết nối được Backend. Kiểm tra lại Terminal uvicorn nhé!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Header style={{ background: '#001529', padding: '0 20px' }}>
        <Title level={3} style={{ color: 'white', margin: '15px 0' }}>Đồ Án Nhóm 9</Title>
      </Header>
      <Content style={{ padding: '50px', display: 'flex', justifyContent: 'center' }}>
        <Card style={{ width: 450, borderRadius: '12px', textAlign: 'center' }}>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Title level={2}>Dự Đoán Kết Quả</Title>
            <Text type="secondary">Chào Khoa, đây là giao diện kết nối thử nghiệm FE và BE.</Text>
            <Button type="primary" size="large" onClick={testBackend} loading={loading} block>
              Bấm để kết nối thử với Backend
            </Button>
          </Space>
        </Card>
      </Content>
      <Footer style={{ textAlign: 'center' }}>Nhóm 9 - Dự đoán kết quả học tập ©2026</Footer>
    </Layout>
  );
}

export default App;