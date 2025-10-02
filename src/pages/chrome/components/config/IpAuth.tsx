import { Table, Modal, Button, Typography, Form, Input, } from 'antd'
import { useBoolean, useToggle, useUpdateEffect } from 'ahooks'
import { useState } from 'react';

const { Text } = Typography
export default function IpAuth() {
    const [form] = Form.useForm()
    const [open, { setTrue, setFalse }] = useBoolean();
    const [ip, setIp] = useState([]);
    const [myip, setMyip] = useState();
    const [loading, { toggle: toggleLoading, }] = useToggle()
    const [loadingAdd, { toggle: toggleAddLoading }] = useToggle()

    const initData = async () => {
        try {
            toggleLoading();
            const [my_ip, ipauthorization]: any = await Promise.all([
                window.py.webshare.my_ip(),
                window.py.webshare.get_ipauthorization()
            ])
            toggleLoading();
            setMyip(my_ip.data.ip_address)
            setIp(ipauthorization.data.results)
        } catch (error) {
            toggleLoading();
            window.message.error('获取数据失败', error?.message)
        }
    }
    const get_ip = async () => {
        try {
            const ipauthorization: any = await window.py.webshare.get_ipauthorization()
            setIp(ipauthorization.data.results)
        } catch (error) {
            window.message.error('获取数据失败', error?.message)
        }
    }
    const onRemove = (row: any) => () => {
        Modal.confirm({
            title: '确定要移除吗？',
            onOk: async () => {
                return new Promise(async (resolve, reject) => {
                    try {
                        await window.py.webshare.remove_ipauthorization(row.id)
                        window.message.success('移除成功')
                        resolve(true)
                    } catch (error) {
                        reject(false)
                    }
                    get_ip()
                })
            }
        })
    }
    const onAdd = async (values: any) => {
        toggleAddLoading()
        try {
            await window.py.webshare.add_ipauthorization({ ip_address: values.ip_address })
            form.resetFields()
            window.message.success('添加成功')
            setFalse()
        } catch (error) {
            console.log('error', error);
            window.message.error('添加失败', error?.message)
        }
        toggleAddLoading()
    }
    useUpdateEffect(() => {
        if (open) {
            initData()
        }
    }, [open])

    return (
        <>
            <Button
                type='link'
                onClick={setTrue}>
                Ip授权
            </Button>
            <Modal
                title={
                    <div>
                        Ip授权
                        {
                            myip &&
                            <span style={{ fontSize: 12, marginLeft: 15 }}>
                                (我的ip: <Text copyable title={myip}>{myip}</Text>)
                                <Button
                                    type='link'
                                    loading={loadingAdd}
                                    onClick={() => {
                                        onAdd({
                                            ip_address: myip
                                        })
                                    }}>
                                    一键授权
                                </Button>
                            </span>
                        }

                    </div>
                }
                open={open}
                onCancel={setFalse}
                footer={null}
                loading={loading}
                destroyOnHidden
            >
                <Form
                    style={{ marginTop: 30 }}
                    form={form}
                    layout='inline'
                    onFinish={(values) => {
                        onAdd(values)
                    }}>
                    <Form.Item label='添加授权IP' name='ip_address' rules={[{ required: true, message: '请输入授权IP' }]}>
                        <Input placeholder='请输入授权IP' disabled={loadingAdd} maxLength={50} />
                    </Form.Item>
                    <Form.Item>
                        <Button
                            loading={loadingAdd}
                            type='primary'
                            onClick={form.submit}>添加</Button>
                    </Form.Item>
                </Form>
                <Table
                    rowKey={'ip_address'}
                    columns={[
                        {
                            title: '已授权的IP',
                            dataIndex: 'ip_address',
                        },
                        {
                            title: '操作',
                            align: 'center',
                            render: (row) => {
                                return (
                                    <Button type='link' onClick={onRemove(row)}>移除</Button>
                                )
                            }
                        },
                    ]}
                    dataSource={ip}
                />
            </Modal>
        </>
    );
}