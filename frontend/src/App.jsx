import React, { useState } from 'react';
import { Form, InputNumber, Button, Card, Typography, Select, Space, message } from 'antd';
import axios from 'axios';

const { Title, Text } = Typography;

const App = () => {
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      // Gửi dữ liệu sang Backend FastAPI
      const response = await axios.post('http://127.0.0.1:8000/predict', values);
      setPrediction(response.data.prediction);
      message.success('Đã dự đoán xong!');
    } catch (error) {
      message.error('Không kết nối được với Backend!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '50px', display: 'flex', justifyContent: 'center', backgroundColor: '#f0f2f5', minHeight: '100vh' }}>
      <Card style={{ width: 500, borderRadius: '15px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        <Title level={3} style={{ textAlign: 'center', color: '#1890ff' }}>Dự Đoán Kết Quả Học Tập</Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: '20px', textAlign: 'center' }}>
          Nhập thông tin sinh viên để hệ thống AI phân tích
        </Text>

        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item label="Số giờ học/tuần" name="study_hours" rules={[{ required: true, message: 'Vui lòng nhập số giờ!' }]}>
            <InputNumber min={0} max={168} style={{ width: '100%' }} placeholder="Ví dụ: 20" />
          </Form.Item>

          <Form.Item label="Điểm trung bình hiện tại" name="previous_score" rules={[{ required: true, message: 'Vui lòng nhập điểm!' }]}>
            <InputNumber min={0} max={10} step={0.1} style={{ width: '100%' }} placeholder="Ví dụ: 7.5" />
          </Form.Item>

          <Form.Item label="Tỷ lệ chuyên cần (%)" name="attendance" rules={[{ required: true, message: 'Vui lòng nhập tỷ lệ!' }]}>
            <InputNumber min={0} max={100} style={{ width: '100%' }} placeholder="Ví dụ: 95" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block size="large" style={{ borderRadius: '8px' }}>
              Bắt đầu dự đoán
            </Button>
          </Form.Item>
        </Form>

        {prediction && (
  <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#e6f7ff', borderRadius: '8px' }}>
    <Title level={4}>Kết quả: {prediction}</Title>
    {/* Thêm 2 dòng này để hiện đầy đủ dữ liệu từ Backend mới */}
    <Text strong>Điểm dự kiến: {response.data.predicted_score}</Text> <br/>
    <Text italic>Lời khuyên: {response.data.advice}</Text>
  </div>
)}
      </Card>
    </div>
  );
};

export default App;