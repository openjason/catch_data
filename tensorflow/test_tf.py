import numpy as np
import tensorflow as tf

# 定义可训练模型变量
W = tf.Variable([.3], tf.float32) #类型为tf.float32初始值为0.3的可训练模型变量W
b = tf.Variable([-.3], tf.float32) #类型为tf.float32初始值为-0.3的可训练模型变量b

# 定义模型的输入输出
x = tf.placeholder(tf.float32) #定义类型为tf.float32的模型输入变量x
linear_model = W * x + b # 定义模型函数，已经模型输出值linear_model

# 定义输出目标变量
y = tf.placeholder(tf.float32)

# 定义距离目标变量的距离
loss = tf.reduce_sum(tf.square(linear_model - y)) # 每个输出值与对应目标值差平方的和

# 定义优化器
optimizer = tf.train.GradientDescentOptimizer(0.01) # 通过以精度0.01的梯度下降
train = optimizer.minimize(loss) # 通过优化器，让其距离目标值逐渐减小

# 准备训练用的数据
x_train = [1,2,3,4] # 输入变量x的值序列
y_train = [0,-1,-2,-3] # 需要能够对应输出的目标值序列

# 开始训练
init = tf.global_variables_initializer() # 初始化可训练变量
sess = tf.Session() # 创建一个session
sess.run(init) # 复位训练模型
for i in range(1000):
  # 喂训练数据
  sess.run(train, {x:x_train, y:y_train})

# 输出训练结果
curr_W, curr_b, curr_loss  = sess.run([W, b, loss], {x:x_train, y:y_train})
print("W: %s b: %s loss: %s"%(curr_W, curr_b, curr_loss))

# 最终结果当 W为-0.9999969、b为0.99999082，距离目标值(每个输出值与目标值差的平方和)为5.69997e-11
# 输出: W: [-0.9999969] b: [0.99999082] loss: 5.69997e-11



#import tensorflow as tf
# Numpy通常用于加载，维护与预处理数据
#import numpy as np
# 需求队列(还有很多其他类型的column)
features = [tf.contrib.layers.real_valued_column("x", dimension=1)]
# estimator是一个前端调用用于训练与评估的接口，这里有非常多预定义的类型，如Linear Regression, Logistic Regression, Linear Classification, Logistic Classification 以及各种各样的Neural Network Classifiers 与 Regressors. 这里我们用的是Linear Regression
estimator = tf.contrib.learn.LinearRegressor(feature_columns=features)
# TensorFlow有提供了许多工具方法来读写数据集，这里我们使用`numpy_input_fn`，我们不得不告诉方法一共有多少组(num_epochs)，并且每组有多大(batch_size)
x = np.array([1., 2., 3., 4.])
y = np.array([0., -1., -2., -3.])
input_fn = tf.contrib.learn.io.numpy_input_fn({"x":x}, y, batch_size=4,
                                              num_epochs=1000)
# 我们可以通过传入训练所用的数据集调用1000次`fit`方法来一步步训练
estimator.fit(input_fn=input_fn, steps=1000)
# 评估目前模型训练的怎么样。实际运用中，我们需要一个独立的验证与测试数据集避免训练过渡(overfitting)
estimator.evaluate(input_fn=input_fn)