import numpy as np
import tensorflow as tf

# Just disables the warning, doesn't enable AVX/FMA
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 定义需求队列(这里我们只需要一个featurex)
def model(features, labels, mode):
  # 构建线性模型
  W = tf.get_variable("W", [1], dtype=tf.float64)
  b = tf.get_variable("b", [1], dtype=tf.float64)
  y = W*features['x'] + b
  # 定义距离目标变量的距离
  loss = tf.reduce_sum(tf.square(y - labels))
  # 训练子图
  global_step = tf.train.get_global_step()
  optimizer = tf.train.GradientDescentOptimizer(0.01)
  train = tf.group(optimizer.minimize(loss),
                   tf.assign_add(global_step, 1))
  # ModelFnOps用于将各参数串起来
  return tf.contrib.learn.ModelFnOps(
      mode=mode, predictions=y,
      loss=loss,
      train_op=train)

estimator = tf.contrib.learn.Estimator(model_fn=model)
# 定义我们的训练用的数据集
x = np.array([1., 2., 3., 4.])
y = np.array([0., -1., -2., -3.])
input_fn = tf.contrib.learn.io.numpy_input_fn({"x": x}, y, 4, num_epochs=1000)

# 训练
estimator.fit(input_fn=input_fn, steps=1000)
# 评估训练模型
print(estimator.evaluate(input_fn=input_fn, steps=10))