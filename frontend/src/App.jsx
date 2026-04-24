import React, { useState, useEffect } from 'react';
import { Form, InputNumber, Button, Card, Typography, Table, message, Tag, Row, Col, Select } from 'antd';
import axios from 'axios';
import './App.css'; // Import file CSS bên ngoài

const { Title, Text } = Typography;
const { Option } = Select;

const App = () => {
  const [loading, setLoading] = useState(false);
  const [predictionData, setPredictionData] = useState(null);
  const [history, setHistory] = useState([]);

  const fetchHistory = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/history');
      setHistory(res.data);
    } catch (error) {
      console.error("Không lấy được lịch sử:", error);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:8000/predict', values);
      setPredictionData(response.data);
      message.success('Đã dự đoán xong!');
      fetchHistory(); 
    } catch (error) {
      message.error('Lỗi kết nối Backend!');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { title: 'Giờ học', dataIndex: 'study_hours', key: 'study_hours' },
    { title: 'Điểm G2', dataIndex: 'previous_score', key: 'previous_score' },
    { title: 'Vắng', dataIndex: 'attendance', key: 'attendance' },
    { title: 'Rớt môn', dataIndex: 'failures', key: 'failures' },
    { 
      title: 'Kết quả', 
      dataIndex: 'result', 
      key: 'result',
      render: (text) => (
        <Tag color={text === 'PASS' ? 'green' : 'red'}>{text}</Tag>
      )
    },
    { title: 'Dự đoán', dataIndex: 'score', key: 'score', render: (val) => <b>{val}</b> },
    { title: 'Ngày thực hiện', dataIndex: 'date', key: 'date' },
  ];

  return (
    <div className="main-container">
      <div className="content-wrapper">
        
        <Card className="prediction-card">
          <Title level={3} className="main-title">Hệ Thống Dự Đoán Kết Quả Học Tập</Title>
          <Text type="secondary" className="sub-title">
            Nhóm 9 - AI Academic Performance Prediction
          </Text>

          <Form layout="vertical" onFinish={onFinish} initialValues={{ failures: 0, goout: 3 }}>
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item label="Số giờ học/tuần" name="study_hours" rules={[{ required: true }]}>
                  <InputNumber min={1} max={4} className="full-width" placeholder="Thang 1-4" />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item label="Điểm kỳ trước (G2)" name="previous_score" rules={[{ required: true }]}>
                  <InputNumber min={0} max={20} step={0.5} className="full-width" placeholder="Thang 0-20" />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item label="Số buổi vắng" name="attendance" rules={[{ required: true }]}>
                  <InputNumber min={0} max={93} className="full-width" placeholder="0 - 93" />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item label="Số môn từng rớt" name="failures">
                  <Select placeholder="Chọn số môn">
                    <Option value={0}>Chưa từng rớt</Option>
                    <Option value={1}>1 môn</Option>
                    <Option value={2}>2 môn</Option>
                    <Option value={3}>3 môn trở lên</Option>
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="Mức độ đi chơi" name="goout">
                  <Select>
                    <Option value={1}>Rất ít</Option>
                    <Option value={2}>Ít</Option>
                    <Option value={3}>Trung bình</Option>
                    <Option value={4}>Nhiều</Option>
                    <Option value={5}>Rất nhiều</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} block size="large" className="submit-btn">
                Bắt đầu phân tích AI
              </Button>
            </Form.Item>
          </Form>

          {predictionData && (
            <div className={`result-box ${predictionData.prediction === 'PASS' ? 'pass' : 'fail'}`}>
              <Title level={4} className="result-status">
                Kết quả: {predictionData.prediction}
              </Title>
              <Text strong className="result-score">Điểm số dự kiến: {predictionData.score}/20</Text> <br/>
              <Text italic className="result-advice">Lời khuyên: {predictionData.advice}</Text>
            </div>
          )}
        </Card>

        <Card title="Lịch sử dự đoán (Database)" className="history-card">
          <Table 
            dataSource={history} 
            columns={columns} 
            rowKey="id" 
            pagination={{ pageSize: 5 }} 
          />
        </Card>
      </div>
    </div>
  );
};

export default App;